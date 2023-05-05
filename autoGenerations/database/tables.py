from __future__ import annotations
from typing import List, Union, Dict, Any
from database.utils import Base, make_engine, merge_lists
from database.enums import Etsy, OrderStatus, Prodigi
from database.namespaces import EtsyReceiptSpace, EtsyReceiptShipmentSpace, EtsySellerSpace, EtsyBuyerSpace, \
    EtsyTransactionSpace, AddressSpace, EtsyProductPropertySpace, EtsyProductSpace, EtsyShippingProfileSpace, \
    EtsyProductionPartnerSpace, EtsyListingSpace, EtsyOfferingSpace, EtsyShopSectionSpace, EtsyReturnPolicySpace, \
    EtsyShippingProfileUpgradeSpace, EtsyShippingProfileDestinationSpace, EtsyShopSpace, ProdigiAddressSpace, \
    EtsyRefundSpace, ProdigiOrderSpace, ProdigiChargeSpace, ProdigiShipmentSpace, ProdigiShipmentItemSpace,\
    ProdigiFulfillmentLocationSpace, ProdigiRecipientSpace, ProdigiItemSpace, ProdigiCostSpace, ProdigiAssetSpace,\
    ProdigiPackingSlipSpace, ProdigiChargeItemSpace, ProdigiStatusSpace, ProdigiIssueSpace, \
    ProdigiAuthorizationDetailsSpace, ProdigiShipmentDetailSpace, ProdigiAddressSpace

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, ForeignKey, Enum, Table, DateTime

transaction_product_data_association_table = Table(
    "transaction_product_data_association_table",
    Base.metadata,
    Column("transaction_id", ForeignKey("etsy_transaction.id"), primary_key=True),
    Column("product_data_id", ForeignKey("etsy_product_property.id"), primary_key=True)
)

listing_production_partner_association_table = Table(
    "listing_production_partner_association_table",
    Base.metadata,
    Column("listing_id", ForeignKey("etsy_listing.id"), primary_key=True),
    Column("production_partner_id", ForeignKey("etsy_production_partner.id"), primary_key=True)
)

listing_product_association_table = Table(
    "listing_product_association_table",
    Base.metadata,
    Column("listing_id", ForeignKey("etsy_listing.id"), primary_key=True),
    Column("product_id", ForeignKey("etsy_product.id"), primary_key=True)
)

buyer_address_association_table = Table(
    "buyer_address_association_table",
    Base.metadata,
    Column("buyer_id", ForeignKey("etsy_buyer.id"), primary_key=True),
    Column("address_id", ForeignKey("address.id"), primary_key=True)
)

recipient_address_association_table = Table(
    "recipient_address_association_table",
    Base.metadata,
    Column("recipient_id", ForeignKey("prodigi_recipient.id"), primary_key=True),
    Column("address_id", ForeignKey("address.id"), primary_key=True)
)

item_asset_association_table = Table(
    "item_asset_association_table",
    Base.metadata,
    Column("item_id", ForeignKey("prodigi_item.id"), primary_key=True),
    Column("asset_id", ForeignKey("prodigi_asset.id"), primary_key=True)
)

# Thread on SQL UPDATE when you are 'changing' a table column value to the value it already is:
# https://www.sqlservercentral.com/forums/topic/update-when-the-values-are-the-same. Apparently SQL
# still marks the disk record as dirty and sends an update... maybe. So have to do check in all of the update methods to
# make most efficient transaction. Better safe than inefficient


class EtsyReceipt(Base):
    """
    API Reference: https://developer.etsy.com/documentation/reference#operation/getShopReceipt
    """
    __tablename__ = 'etsy_receipt'
    id = Column(Integer, primary_key=True)
    receipt_id = Column(BigInteger, unique=True)
    receipt_type = Column(Integer)
    status = Column(Enum(Etsy.OrderStatus))
    order_status = Column(Enum(OrderStatus))
    needs_fulfillment = Column(Boolean, default=False)
    payment_method = Column(String)
    message_from_seller = Column(String)
    message_from_buyer = Column(String)
    message_from_payment = Column(String)
    is_paid = Column(Boolean)
    is_shipped = Column(Boolean)
    create_timestamp = Column(DateTime)
    created_timestamp = Column(DateTime)
    update_timestamp = Column(DateTime)
    updated_timestamp = Column(DateTime)
    is_gift = Column(Boolean)
    gift_message = Column(String)
    grand_total = Column(Integer)
    grand_total_divisor = Column(Integer)
    grand_total_currency_code = Column(String)
    sub_total = Column(Integer)
    sub_total_divisor = Column(Integer)
    sub_total_currency_code = Column(String)
    total_price = Column(Integer)
    total_price_divisor = Column(Integer)
    total_price_currency_code = Column(String)
    shipping_cost = Column(Integer)
    shipping_cost_divisor = Column(Integer)
    shipping_cost_currency_code = Column(String)
    tax_cost = Column(Integer)
    tax_cost_divisor = Column(Integer)
    tax_cost_currency_code = Column(String)
    vat_cost = Column(Integer)
    vat_cost_divisor = Column(Integer)
    vat_cost_currency_code = Column(String)
    discount = Column(Integer)
    discount_divisor = Column(Integer)
    discount_currency_code = Column(String)
    gift_wrap_price = Column(Integer)
    gift_wrap_price_divisor = Column(Integer)
    gift_wrap_price_currency_code = Column(String)

    # relationships

    # many to one
    _address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship("Address", uselist=False, back_populates='receipts')
    _buyer_id = Column(Integer, ForeignKey('etsy_buyer.id'))
    buyer = relationship("EtsyBuyer", uselist=False, back_populates='receipts')
    _seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates='receipts')

    # one to many
    prodigi_orders = relationship("ProdigiOrder", back_populates="etsy_receipt", cascade="all, delete, delete-orphan")
    transactions = relationship("EtsyTransaction", back_populates='receipt', cascade="all, delete, delete-orphan")
    receipt_shipments = relationship("EtsyReceiptShipment", back_populates='receipt',
                                     cascade="all, delete, delete-orphan")
    refunds = relationship("EtsyRefund", back_populates="receipt", cascade="all, delete, delete-orphan")

    @classmethod
    def create(cls, receipt_data: Union[EtsyReceiptSpace, Dict[str, Any]],
               order_status: OrderStatus = None,
               needs_fulfillment: bool = None,
               address: Address = None,
               buyer: EtsyBuyer = None,
               seller: EtsySeller = None,
               transactions: List[EtsyTransaction] = None,
               receipt_shipments: List[EtsyReceiptShipment] = None,
               prodigi_orders: List[ProdigiOrder] = None,
               refunds: List[EtsyRefund] = None
               ) -> EtsyReceipt:
        if not isinstance(receipt_data, EtsyReceiptSpace):
            receipt_data = cls.create_namespace(receipt_data)

        receipt = cls(
            receipt_id=receipt_data.receipt_id,
            receipt_type=receipt_data.receipt_type,
            status=receipt_data.status,
            payment_method=receipt_data.payment_method,
            message_from_seller=receipt_data.message_from_seller,
            message_from_buyer=receipt_data.message_from_buyer,
            message_from_payment=receipt_data.message_from_payment,
            is_paid=receipt_data.is_paid,
            is_shipped=receipt_data.is_shipped,
            create_timestamp=receipt_data.create_timestamp,
            created_timestamp=receipt_data.created_timestamp,
            update_timestamp=receipt_data.update_timestamp,
            updated_timestamp=receipt_data.updated_timestamp,
            is_gift=receipt_data.is_gift,
            gift_message=receipt_data.gift_message,
            grand_total=receipt_data.grand_total,
            grand_total_divisor=receipt_data.grand_total_divisor,
            grand_total_currency_code=receipt_data.grand_total_currency_code,
            sub_total=receipt_data.sub_total,
            sub_total_divisor=receipt_data.sub_total_divisor,
            sub_total_currency_code=receipt_data.sub_total_currency_code,
            total_price=receipt_data.total_price,
            total_price_divisor=receipt_data.total_price_divisor,
            total_price_currency_code=receipt_data.total_price_currency_code,
            shipping_cost=receipt_data.shipping_cost,
            shipping_cost_divisor=receipt_data.shipping_cost_divisor,
            shipping_cost_currency_code=receipt_data.shipping_cost_currency_code,
            tax_cost=receipt_data.tax_cost,
            tax_cost_divisor=receipt_data.tax_cost_divisor,
            tax_cost_currency_code=receipt_data.tax_cost_currency_code,
            vat_cost=receipt_data.vat_cost,
            vat_cost_divisor=receipt_data.vat_cost_divisor,
            vat_cost_currency_code=receipt_data.vat_cost_currency_code,
            discount=receipt_data.discount,
            discount_divisor=receipt_data.discount_divisor,
            discount_currency_code=receipt_data.discount_currency_code,
            gift_wrap_price=receipt_data.gift_wrap_price,
            gift_wrap_price_divisor=receipt_data.gift_wrap_price_divisor,
            gift_wrap_price_currency_code=receipt_data.gift_wrap_price_currency_code
        )

        if order_status is not None:
            receipt.order_status = order_status

        if needs_fulfillment is not None:
            receipt.needs_fulfillment = needs_fulfillment

        if address is not None:
            receipt.address = address

        if buyer is not None:
            receipt.buyer = buyer

        if seller is not None:
            receipt.seller = seller

        if transactions is not None:
            receipt.transactions = transactions

        if receipt_shipments is not None:
            receipt.receipt_shipments = receipt_shipments

        if prodigi_orders is not None:
            receipt.prodigi_orders = prodigi_orders

        if refunds is not None:
            receipt.refunds = refunds

        return receipt

    @staticmethod
    def create_namespace(etsy_receipt: Dict[str, Any]) -> EtsyReceiptSpace:
        return EtsyReceiptSpace(etsy_receipt)

    @staticmethod
    def get_existing(session, receipt_id: int) -> Union[None, EtsyReceipt]:
        return session.query(EtsyReceipt).filter(EtsyReceipt.receipt_id == int(receipt_id)).first()

    def update(self, receipt_data: Union[EtsyReceiptSpace, Dict[str, Any]] = None,
               order_status: OrderStatus = None,
               needs_fulfillment: bool = None,
               address: Address = None,
               buyer: EtsyBuyer = None,
               seller: EtsySeller = None,
               transactions: List[EtsyTransaction] = None,
               receipt_shipments: List[EtsyReceiptShipment] = None,
               prodigi_orders: List[ProdigiOrder] = None,
               refunds: List[EtsyRefund] = None,
               overwrite_list: bool = False
               ):
        if receipt_data is not None:
            if not isinstance(receipt_data, EtsyReceiptSpace):
                receipt_data = self.create_namespace(receipt_data)

            if self.receipt_type != receipt_data.receipt_type:
                self.receipt_type = receipt_data.receipt_type
            if self.status != receipt_data.status:
                self.status = receipt_data.status
            if self.payment_method != receipt_data.payment_method:
                self.payment_method = receipt_data.payment_method
            if self.message_from_seller != receipt_data.message_from_seller:
                self.message_from_seller = receipt_data.message_from_seller
            if self.message_from_buyer != receipt_data.message_from_buyer:
                self.message_from_buyer = receipt_data.message_from_buyer
            if self.message_from_payment != receipt_data.message_from_payment:
                self.message_from_payment = receipt_data.message_from_payment
            if self.is_paid != receipt_data.is_paid:
                self.is_paid = receipt_data.is_paid
            if self.is_shipped != receipt_data.is_shipped:
                self.is_shipped = receipt_data.is_shipped
            if self.create_timestamp != receipt_data.create_timestamp:
                self.create_timestamp = receipt_data.create_timestamp
            if self.created_timestamp != receipt_data.created_timestamp:
                self.created_timestamp = receipt_data.created_timestamp
            if self.update_timestamp != receipt_data.update_timestamp:
                self.update_timestamp = receipt_data.update_timestamp
            if self.update_timestamp != receipt_data.updated_timestamp:
                self.updated_timestamp = receipt_data.updated_timestamp
            if self.is_gift != receipt_data.is_gift:
                self.is_gift = receipt_data.is_gift
            if self.gift_message != receipt_data.gift_message:
                self.gift_message = receipt_data.gift_message
            if self.grand_total != receipt_data.grand_total:
                self.grand_total = receipt_data.grand_total
            if self.grand_total_divisor != receipt_data.grand_total_divisor:
                self.grand_total_divisor = receipt_data.grand_total_divisor
            if self.grand_total_currency_code != receipt_data.grand_total_currency_code:
                self.grand_total_currency_code = receipt_data.grand_total_currency_code
            if self.sub_total != receipt_data.sub_total:
                self.sub_total = receipt_data.sub_total
            if self.sub_total_divisor != receipt_data.sub_total_divisor:
                self.sub_total_divisor = receipt_data.sub_total_divisor
            if self.sub_total_currency_code != receipt_data.sub_total_currency_code:
                self.sub_total_currency_code = receipt_data.sub_total_currency_code
            if self.total_price != receipt_data.total_price:
                self.total_price = receipt_data.total_price
            if self.total_price_divisor != receipt_data.total_price_divisor:
                self.total_price_divisor = receipt_data.total_price_divisor
            if self.total_price_currency_code != receipt_data.total_price_currency_code:
                self.total_price_currency_code = receipt_data.total_price_currency_code
            if self.shipping_cost != receipt_data.shipping_cost:
                self.shipping_cost = receipt_data.shipping_cost
            if self.shipping_cost_divisor != receipt_data.shipping_cost_divisor:
                self.shipping_cost_divisor = receipt_data.shipping_cost_divisor
            if self.shipping_cost_currency_code != receipt_data.shipping_cost_currency_code:
                self.shipping_cost_currency_code = receipt_data.shipping_cost_currency_code
            if self.tax_cost != receipt_data.tax_cost:
                self.tax_cost = receipt_data.tax_cost
            if self.tax_cost_divisor != receipt_data.tax_cost_divisor:
                self.tax_cost_divisor = receipt_data.tax_cost_divisor
            if self.tax_cost_currency_code != receipt_data.tax_cost_currency_code:
                self.tax_cost_currency_code = receipt_data.tax_cost_currency_code
            if self.vat_cost != receipt_data.vat_cost:
                self.vat_cost = receipt_data.vat_cost
            if self.vat_cost_divisor != receipt_data.vat_cost_divisor:
                self.vat_cost_divisor = receipt_data.vat_cost_divisor
            if self.vat_cost_currency_code != receipt_data.vat_cost_currency_code:
                self.vat_cost_currency_code = receipt_data.vat_cost_currency_code
            if self.discount != receipt_data.discount:
                self.discount = receipt_data.discount
            if self.discount_divisor != receipt_data.discount_divisor:
                self.discount_divisor = receipt_data.discount_divisor
            if self.discount_currency_code != receipt_data.discount_currency_code:
                self.discount_currency_code = receipt_data.discount_currency_code
            if self.gift_wrap_price != receipt_data.gift_wrap_price:
                self.gift_wrap_price = receipt_data.gift_wrap_price
            if self.gift_wrap_price_divisor != receipt_data.gift_wrap_price_divisor:
                self.gift_wrap_price_divisor = receipt_data.gift_wrap_price_divisor
            if self.gift_wrap_price_currency_code != receipt_data.gift_wrap_price_currency_code:
                self.gift_wrap_price_currency_code = receipt_data.gift_wrap_price_currency_code

        if order_status is not None and self.order_status != order_status:
            self.order_status = order_status

        if needs_fulfillment is not None and self.needs_fulfillment != needs_fulfillment:
            self.needs_fulfillment = needs_fulfillment

        if address is not None and self.address != address:
            self.address = address

        if buyer is not None and self.buyer != buyer:
            self.buyer = buyer

        if seller is not None and self.seller != seller:
            self.seller = seller

        if transactions is not None:
            self.transactions = transactions if overwrite_list else merge_lists(self.transactions, transactions)

        if receipt_shipments is not None:
            self.receipt_shipments = receipt_shipments if overwrite_list else merge_lists(
                self.receipt_shipments, receipt_shipments)

        if prodigi_orders is not None:
            self.prodigi_orders = prodigi_orders if overwrite_list else merge_lists(self.prodigi_orders, prodigi_orders)

        if refunds is not None:
            self.refunds = refunds if overwrite_list else merge_lists(self.refunds, refunds)


class EtsySeller(Base):
    __tablename__ = 'etsy_seller'
    id = Column(Integer, primary_key=True)
    seller_id = Column(BigInteger, unique=True)
    email = Column(String)

    # relationships

    # one to many
    receipts = relationship('EtsyReceipt', back_populates='seller')
    transactions = relationship("EtsyTransaction", back_populates='seller')
    listings = relationship("EtsyListing", back_populates='seller')
    shipping_profiles = relationship("EtsyShippingProfile", back_populates='seller')
    shop_sections = relationship("EtsyShopSection", back_populates="seller")
    shops = relationship("EtsyShop", back_populates="seller")

    @classmethod
    def create(cls, seller_data: Union[EtsySellerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None,
               transactions: List[EtsyTransaction] = None,
               listings: List[EtsyListing] = None,
               shipping_profiles: List[EtsyShippingProfile] = None,
               shop_sections: List[EtsyShopSection] = None,
               shops: List[EtsyShop] = None
               ) -> EtsySeller:
        if not isinstance(seller_data, EtsySellerSpace):
            seller_data = cls.create_namespace(seller_data)

        seller = cls(
            seller_id=seller_data.seller_id,
            email=seller_data.email
        )

        if receipts is not None:
            seller.receipts = receipts

        if transactions is not None:
            seller.transactions = transactions

        if listings is not None:
            seller.listings = listings

        if shipping_profiles is not None:
            seller.shipping_profiles = shipping_profiles

        if shop_sections is not None:
            seller.shop_sections = shop_sections

        if shops is not None:
            seller.shops = shops

        return seller

    @staticmethod
    def create_namespace(seller_data: Dict[str, Any]):
        return EtsySellerSpace(seller_data)

    @staticmethod
    def get_existing(session, seller_id: int) -> Union[None, EtsySeller]:
        return session.query(EtsySeller).filter(
            EtsySeller.seller_id == int(seller_id)
        ).first()

    def update(self, seller_data: Union[EtsySellerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None,
               transactions: List[EtsyTransaction] = None,
               listings: List[EtsyListing] = None,
               shipping_profiles: List[EtsyShippingProfile] = None,
               shop_sections: List[EtsyShopSection] = None,
               shops: List[EtsyShop] = None,
               overwrite_list: bool = False):
        if not isinstance(seller_data, EtsySellerSpace):
            seller_data = self.create_namespace(seller_data)

        if self.email != seller_data.email:
            self.email = seller_data.email

        if receipts is not None:
            self.receipts = receipts if overwrite_list else merge_lists(self.receipts, receipts)

        if transactions:
            self.transactions = transactions if overwrite_list else merge_lists(self.transactions, transactions)

        if listings is not None:
            self.listings = listings if overwrite_list else merge_lists(self.listings, listings)

        if shipping_profiles is not None:
            self.shipping_profiles = shipping_profiles if overwrite_list else merge_lists(self.shipping_profiles,
                                                                                          shipping_profiles)

        if shop_sections is not None:
            self.shop_sections = shop_sections if overwrite_list else merge_lists(self.shop_sections, shop_sections)

        if shops is not None:
            self.shops = shops if overwrite_list else merge_lists(self.shops, shops)


class EtsyBuyer(Base):
    __tablename__ = 'etsy_buyer'
    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id = Column(BigInteger, unique=True)
    email = Column(String)
    name = Column(String)

    # relationships

    # one to many
    receipts = relationship('EtsyReceipt', back_populates='buyer')
    transactions = relationship("EtsyTransaction", back_populates='buyer')

    # many to many
    addresses: Mapped[List[Address]] = relationship(
        secondary=buyer_address_association_table, back_populates='buyers')

    @classmethod
    def create(cls, buyer_data: Union[EtsyBuyerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None,
               transactions: List[EtsyTransaction] = None,
               addresses: List[Address] = None
               ) -> EtsyBuyer:
        if not isinstance(buyer_data, EtsyBuyerSpace):
            buyer_data = cls.create_namespace(buyer_data)

        buyer = cls(
            buyer_id=buyer_data.buyer_id,
            email=buyer_data.email,
            name=buyer_data.name
        )

        if receipts is not None:
            buyer.receipts = receipts

        if transactions is not None:
            buyer.transactions = transactions

        if addresses is not None:
            buyer.addresses = addresses

        return buyer

    @staticmethod
    def create_namespace(buyer_data: Dict[str, Any]):
        return EtsyBuyerSpace(buyer_data)

    @staticmethod
    def get_existing(session, buyer_id: int) -> Union[None, EtsyBuyer]:
        return session.query(EtsyBuyer).filter(
            EtsyBuyer.buyer_id == int(buyer_id)
        ).first()

    def update(self, buyer_data: Union[EtsyBuyerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None,
               transactions: List[EtsyTransaction] = None,
               addresses: List[Address] = None,
               overwrite_list: bool = False):
        if not isinstance(buyer_data, EtsyBuyerSpace):
            buyer_data = self.create_namespace(buyer_data)

        if self.email != buyer_data.email:
            self.email = buyer_data.email
        if self.name != buyer_data.name:
            self.name = buyer_data.name

        if receipts is not None:
            self.receipts = receipts if overwrite_list else merge_lists(self.receipts, receipts)

        if transactions:
            self.transactions = transactions if overwrite_list else merge_lists(self.transactions, transactions)

        if addresses is not None:
            self.addresses = addresses if overwrite_list else merge_lists(self.addresses, addresses)


class Address(Base):
    __tablename__ = 'address'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_line = Column(String)
    second_line = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String)
    formatted = Column(String)

    # relationships

    # one to many
    receipts = relationship('EtsyReceipt', back_populates='address')

    # many to many
    buyers: Mapped[List[EtsyBuyer]] = relationship(
        secondary=buyer_address_association_table, back_populates='addresses')
    prodigi_recipients: Mapped[List[ProdigiRecipient]] = relationship(
        secondary=recipient_address_association_table, back_populates='addresses')

    @classmethod
    def create(cls, address_data: Union[AddressSpace, ProdigiAddressSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None,
               buyers: List[EtsyBuyer] = None) -> Address:
        if not isinstance(address_data, (AddressSpace, ProdigiAddressSpace)):
            address_data = cls.create_namespace(address_data)

        address = Address(
            first_line=address_data.first_line,
            second_line=address_data.second_line,
            city=address_data.city,
            state=address_data.state,
            zip_code=address_data.zip,
            country=address_data.country
        )

        if hasattr(address_data, 'formatted_address'):
            address.formatted = address_data.formatted_address

        if receipts is not None:
            address.receipts = receipts

        if buyers is not None:
            address.buyers = buyers

        return address

    def update(self, buyers: List[EtsyBuyer], overwrite_list: bool = False):
        self.buyers = buyers if overwrite_list else merge_lists(self.buyers, buyers)

    @staticmethod
    def create_namespace(address_data: Dict[str, Any]):
        return AddressSpace(address_data)

    @staticmethod
    def get_existing(session, zip_code: str, city: str, state: str, country: str, first_line: str,
                     second_line: str) -> Union[None, Address]:
        return session.query(Address).filter(
            Address.zip_code == zip_code,
            Address.city == city,
            Address.state == state,
            Address.country == country,
            Address.first_line == first_line,
            Address.second_line == second_line
        ).first()


class EtsyTransaction(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getShopReceiptTransaction
    """
    __tablename__ = 'etsy_transaction'
    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id = Column(BigInteger, unique=True)
    title = Column(String)
    description = Column(String)
    create_timestamp = Column(DateTime)
    paid_timestamp = Column(DateTime)
    shipped_timestamp = Column(DateTime)
    quantity = Column(Integer)
    is_digital = Column(Boolean)
    file_data = Column(String)
    transaction_type = Column(String)
    price = Column(Integer)
    price_divisor = Column(Integer)
    price_currency_code = Column(String)
    shipping_cost = Column(Integer)
    shipping_cost_divisor = Column(Integer)
    shipping_cost_currency_code = Column(String)
    min_processing_days = Column(Integer)
    max_processing_days = Column(Integer)
    shipping_method = Column(String)
    shipping_upgrade = Column(String)
    expected_ship_date = Column(DateTime)
    buyer_coupon = Column(Integer)
    shop_coupon = Column(Integer)

    # relationships

    # many to one
    _shipping_profile_id = Column(Integer, ForeignKey('etsy_shipping_profile.id'))
    shipping_profile = relationship('EtsyShippingProfile', uselist=False, back_populates='transactions')
    _receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
    receipt = relationship('EtsyReceipt', uselist=False, back_populates='transactions')
    _buyer_id = Column(Integer, ForeignKey('etsy_buyer.id'))
    buyer = relationship('EtsyBuyer', uselist=False, back_populates='transactions')
    _seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship('EtsySeller', uselist=False, back_populates='transactions')
    _product_id = Column(Integer, ForeignKey('etsy_product.id'))
    product = relationship('EtsyProduct', uselist=False, back_populates='transactions')

    # many to many
    product_properties: Mapped[List[EtsyProductProperty]] = relationship(
        secondary=transaction_product_data_association_table, back_populates='transactions')

    @classmethod
    def create(cls, transaction_data: Union[EtsyTransactionSpace, Dict[str, Any]],
               buyer: EtsyBuyer = None,
               seller: EtsySeller = None,
               product: EtsyProduct = None,
               shipping_profile: EtsyShippingProfile = None,
               receipt: EtsyReceipt = None,
               product_properties: List[EtsyProductProperty] = None) -> EtsyTransaction:
        if not isinstance(transaction_data, EtsyTransactionSpace):
            transaction_data = cls.create_namespace(transaction_data)

        transaction = EtsyTransaction(
            transaction_id=transaction_data.transaction_id,
            title=transaction_data.title,
            description=transaction_data.description,
            create_timestamp=transaction_data.create_timestamp,
            paid_timestamp=transaction_data.paid_timestamp,
            shipped_timestamp=transaction_data.shipped_timestamp,
            quantity=transaction_data.quantity,
            is_digital=transaction_data.is_digital,
            file_data=transaction_data.file_data,
            transaction_type=transaction_data.transaction_type,
            price=transaction_data.price,
            price_divisor=transaction_data.price_divisor,
            price_currency_code=transaction_data.price_currency_code,
            shipping_cost=transaction_data.shipping_cost,
            shipping_cost_divisor=transaction_data.shipping_cost_divisor,
            shipping_cost_currency_code=transaction_data.shipping_cost_currency_code,
            min_processing_days=transaction_data.min_processing_days,
            max_processing_days=transaction_data.max_processing_days,
            shipping_method=transaction_data.shipping_method,
            shipping_upgrade=transaction_data.shipping_upgrade,
            expected_ship_date=transaction_data.expected_ship_date,
            buyer_coupon=transaction_data.buyer_coupon,
            shop_coupon=transaction_data.shop_coupon
        )

        if buyer is not None:
            transaction.buyer = buyer

        if seller is not None:
            transaction.seller = seller

        if shipping_profile is not None:
            transaction.shipping_profile = shipping_profile

        if product is not None:
            transaction.product = product

        if receipt is not None:
            transaction.receipt = receipt

        if product_properties is not None:
            transaction.product_properties = product_properties

        return transaction

    @staticmethod
    def create_namespace(etsy_transaction: Dict[str, Any]):
        return EtsyTransactionSpace(etsy_transaction)

    @staticmethod
    def get_existing(session, transaction_id: int) -> Union[None, EtsyTransaction]:
        return session.query(EtsyTransaction).filter(
            EtsyTransaction.transaction_id == int(transaction_id)
        ).first()

    def update(self, transaction_data: Union[EtsyTransactionSpace, Dict[str, Any]] = None,
               buyer: EtsyBuyer = None,
               seller: EtsySeller = None,
               shipping_profile: EtsyShippingProfile = None,
               product: EtsyProduct = None,
               receipt: EtsyReceipt = None,
               product_properties: List[EtsyProductProperty] = None,
               overwrite_list: bool = False):

        if transaction_data is not None:
            if not isinstance(transaction_data, EtsyTransactionSpace):
                transaction_data = self.create_namespace(transaction_data)

            if self.title != transaction_data.title:
                self.title = transaction_data.title
            if self.description != transaction_data.description:
                self.description = transaction_data.description
            if self.create_timestamp != transaction_data.create_timestamp:
                self.create_timestamp = transaction_data.create_timestamp
            if self.paid_timestamp != transaction_data.paid_timestamp:
                self.paid_timestamp = transaction_data.paid_timestamp
            if self.shipped_timestamp != transaction_data.shipped_timestamp:
                self.shipped_timestamp = transaction_data.shipped_timestamp
            if self.quantity != transaction_data.quantity:
                self.quantity = transaction_data.quantity
            if self.is_digital != transaction_data.is_digital:
                self.is_digital = transaction_data.is_digital
            if self.file_data != transaction_data.file_data:
                self.file_data = transaction_data.file_data
            if self.transaction_type != transaction_data.transaction_type:
                self.transaction_type = transaction_data.transaction_type
            if self.price != transaction_data.price:
                self.price = transaction_data.price
            if self.price_divisor != transaction_data.price_divisor:
                self.price_divisor = transaction_data.price_divisor
            if self.price_currency_code != transaction_data.price_currency_code:
                self.price_currency_code = transaction_data.price_currency_code
            if self.shipping_cost != transaction_data.shipping_cost:
                self.shipping_cost = transaction_data.shipping_cost
            if self.shipping_cost_divisor != transaction_data.shipping_cost_divisor:
                self.shipping_cost_divisor = transaction_data.shipping_cost_divisor
            if self.shipping_cost_currency_code != transaction_data.shipping_cost_currency_code:
                self.shipping_cost_currency_code = transaction_data.shipping_cost_currency_code
            if self.min_processing_days != transaction_data.min_processing_days:
                self.min_processing_days = transaction_data.min_processing_days
            if self.max_processing_days != transaction_data.max_processing_days:
                self.max_processing_days = transaction_data.max_processing_days
            if self.shipping_method != transaction_data.shipping_method:
                self.shipping_method = transaction_data.shipping_method
            if self.shipping_upgrade != transaction_data.shipping_upgrade:
                self.shipping_upgrade = transaction_data.shipping_upgrade
            if self.expected_ship_date != transaction_data.expected_ship_date:
                self.expected_ship_date = transaction_data.expected_ship_date
            if self.buyer_coupon != transaction_data.buyer_coupon:
                self.buyer_coupon = transaction_data.buyer_coupon
            if self.shop_coupon != transaction_data.shop_coupon:
                self.shop_coupon = transaction_data.shop_coupon

        if buyer is not None and self.buyer != buyer:
            self.buyer = buyer

        if seller is not None and self.seller != seller:
            self.seller = seller

        if shipping_profile is not None and self.shipping_profile != shipping_profile:
            self.shipping_profile = shipping_profile

        if product is not None and self.product != product:
            self.product = product

        if receipt is not None and self.receipt != receipt:
            self.receipt = receipt

        if product_properties is not None:
            self.product_properties = product_properties if overwrite_list else merge_lists(self.product_properties,
                                                                                            product_properties)


class EtsyProduct(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getListingProduct
    """
    __tablename__ = 'etsy_product'
    id = Column(Integer, primary_key=True)
    product_id = Column(BigInteger, unique=True)
    sku = Column(Integer)
    price = Column(Float)
    is_deleted = Column(Boolean)

    # relationships

    # one to many
    transactions = relationship("EtsyTransaction", back_populates='product')
    offerings = relationship("EtsyOffering", back_populates='product',
                             cascade="all, delete, delete-orphan")
    properties = relationship("EtsyProductProperty", back_populates='product',
                              cascade="all, delete, delete-orphan")

    # many to many
    listings: Mapped[List[EtsyListing]] = relationship(
        secondary=listing_product_association_table, back_populates="products"
    )

    @classmethod
    def create(cls, product_data: Union[EtsyProductSpace, Dict[str, Any]],
               transactions: List[EtsyTransaction] = None,
               offerings: List[EtsyOffering] = None,
               properties: List[EtsyProductProperty] = None,
               listings: List[EtsyListing] = None
               ) -> EtsyProduct:
        if not isinstance(product_data, EtsyProductSpace):
            product_data = cls.create_namespace(product_data)

        product = cls(
            product_id=product_data.product_id,
            sku=product_data.sku,
            is_deleted=product_data.is_deleted
        )

        if transactions is not None:
            product.transactions = transactions

        if offerings is not None:
            product.offerings = offerings

        if properties is not None:
            product.properties = properties

        if listings is not None:
            product.listings = listings

        return product

    @staticmethod
    def create_namespace(product_data: Dict[str, Any]):
        return EtsyProductSpace(product_data)

    @staticmethod
    def get_existing(session, product_id: int) -> Union[None, EtsyProduct]:
        return session.query(EtsyProduct).filter(EtsyProduct.product_id == int(product_id)).first()

    def update(self, product_data: Union[EtsyProductSpace, Dict[str, Any]] = None,
               transactions: List[EtsyTransaction] = None,
               offerings: List[EtsyOffering] = None,
               properties: List[EtsyProductProperty] = None,
               listings: List[EtsyListing] = None,
               overwrite_lists: bool = False
               ):

        if product_data is not None:
            if not isinstance(product_data, EtsyProductSpace):
                product_data = self.create_namespace(product_data)

            if self.sku != product_data.sku:
                self.sku = product_data.sku
            if self.is_deleted != product_data.is_deleted:
                self.is_deleted = product_data.is_deleted

        if transactions is not None:
            self.transactions = transactions if overwrite_lists else merge_lists(self.transactions, transactions)

        if offerings is not None:
            self.offerings = offerings if overwrite_lists else merge_lists(self.offerings, offerings)

        if properties is not None:
            self.properties = properties if overwrite_lists else merge_lists(self.properties, properties)

        if listings is not None:
            self.listings = listings if overwrite_lists else merge_lists(self.listings, listings)


class EtsyShippingProfile(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getShopShippingProfile
    """
    __tablename__ = 'etsy_shipping_profile'
    id = Column(Integer, primary_key=True)
    shipping_profile_id = Column(BigInteger, unique=True)
    title = Column(String)
    min_processing_days = Column(Integer)
    max_processing_days = Column(Integer)
    processing_days_display_label = Column(String)
    origin_country_iso = Column(String)
    is_deleted = Column(Boolean)
    origin_postal_code = Column(String)
    profile_type = Column(Enum(Etsy.ShippingProfileType))
    domestic_handling_fee = Column(Float)
    internation_handling_fee = Column(Float)

    # relationships

    # many to one
    _seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates="shipping_profiles")

    # one to many
    destinations = relationship("EtsyShippingProfileDestination", back_populates='shipping_profile',
                                cascade="all, delete, delete-orphan")
    upgrades = relationship("EtsyShippingProfileUpgrade", back_populates='shipping_profile',
                            cascade="all, delete, delete-orphan")
    transactions = relationship("EtsyTransaction", back_populates='shipping_profile')
    listings = relationship("EtsyListing", back_populates="shipping_profile")

    @classmethod
    def create(cls, shipping_profile_data: Union[EtsyShippingProfileSpace, Dict[str, Any]],
               seller: EtsySeller = None,
               destinations: List[EtsyShippingProfileDestination] = None,
               upgrades: List[EtsyShippingProfileUpgrade] = None,
               transactions: List[EtsyTransaction] = None,
               listings: List[EtsyListing] = None
               ) -> EtsyShippingProfile:
        if not isinstance(shipping_profile_data, EtsyShippingProfileSpace):
            shipping_profile_data = cls.create_namespace(shipping_profile_data)

        shipping_profile = cls(
            shipping_profile_id=shipping_profile_data.shipping_profile_id,
            title=shipping_profile_data.title,
            min_processing_days=shipping_profile_data.min_processing_days,
            max_processing_days=shipping_profile_data.max_processing_days,
            processing_days_display_label=shipping_profile_data.processing_days_display_label,
            origin_country_iso=shipping_profile_data.origin_country_iso,
            is_deleted=shipping_profile_data.is_deleted,
            origin_postal_code=shipping_profile_data.origin_postal_code,
            profile_type=shipping_profile_data.profile_type,
            domestic_handling_fee=shipping_profile_data.domestic_handling_fee,
            internation_handling_fee=shipping_profile_data.international_handling_fee
        )

        if seller is not None:
            shipping_profile.seller = seller

        if destinations is not None:
            shipping_profile.destinations = destinations

        if upgrades is not None:
            shipping_profile.upgrades = upgrades

        if transactions is not None:
            shipping_profile.transactions = transactions

        if listings is not None:
            shipping_profile.listings = listings

        return shipping_profile

    @staticmethod
    def create_namespace(shipping_profile_data: Dict[str, Any]):
        return EtsyShippingProfileSpace(shipping_profile_data)

    @staticmethod
    def get_existing(session, shipping_profile_id: int) -> Union[None, EtsyShippingProfile]:
        return session.query(EtsyShippingProfile).filter(
            EtsyShippingProfile.shipping_profile_id == int(shipping_profile_id)
        ).first()

    def update(self, shipping_profile_data: Union[EtsyShippingProfile, Dict[str, Any]] = None,
               seller: EtsySeller = None,
               destinations: List[EtsyShippingProfileDestination] = None,
               upgrades: List[EtsyShippingProfileUpgrade] = None,
               transactions: List[EtsyTransaction] = None,
               listings: List[EtsyListing] = None,
               overwrite_lists: bool = False
               ):

        if shipping_profile_data is not None:
            if not isinstance(shipping_profile_data, EtsyShippingProfileSpace):
                shipping_profile_data = self.create_namespace(shipping_profile_data)

            if self.title != shipping_profile_data.title:
                self.title = shipping_profile_data.title
            if self.min_processing_days != shipping_profile_data.min_processing_days:
                self.min_processing_days = shipping_profile_data.min_processing_days
            if self.max_processing_days != shipping_profile_data.max_processing_days:
                self.max_processing_days = shipping_profile_data.max_processing_days
            if self.processing_days_display_label != shipping_profile_data.processing_days_display_label:
                self.processing_days_display_label = shipping_profile_data.processing_days_display_label
            if self.origin_country_iso != shipping_profile_data.origin_country_iso:
                self.origin_country_iso = shipping_profile_data.origin_country_iso
            if self.is_deleted != shipping_profile_data.is_deleted:
                self.is_deleted = shipping_profile_data.is_deleted
            if self.origin_postal_code != shipping_profile_data.origin_postal_code:
                self.origin_postal_code = shipping_profile_data.origin_postal_code
            if self.profile_type != shipping_profile_data.profile_type:
                self.profile_type = shipping_profile_data.profile_type
            if self.domestic_handling_fee != shipping_profile_data.domestic_handling_fee:
                self.domestic_handling_fee = shipping_profile_data.domestic_handling_fee
            if self.internation_handling_fee != shipping_profile_data.international_handling_fee:
                self.internation_handling_fee = shipping_profile_data.international_handling_fee

        if seller is not None and self.seller != seller:
            self.seller = seller

        if destinations is not None:
            self.destinations = destinations if overwrite_lists else merge_lists(self.destinations, destinations)

        if upgrades is not None:
            self.upgrades = upgrades if overwrite_lists else merge_lists(self.upgrades, upgrades)

        if transactions is not None:
            self.transactions = transactions if overwrite_lists else merge_lists(self.transactions, transactions)

        if listings is not None:
            self.listings = listings if overwrite_lists else merge_lists(self.listings, listings)


class EtsyShippingProfileDestination(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getShopShippingProfileDestinationsByShippingProfile
    """
    __tablename__ = 'etsy_shipping_profile_destination'
    id = Column(Integer, primary_key=True)
    shipping_profile_destination_id = Column(BigInteger, unique=True)
    origin_country_iso = Column(String)
    destination_country_iso = Column(String)
    destination_region = Column(String)
    primary_cost = Column(Integer)
    primary_cost_divisor = Column(Integer)
    primary_cost_currency_code = Column(String)
    secondary_cost = Column(Integer)
    secondary_cost_divisor = Column(Integer)
    secondary_cost_currency_code = Column(String)

    # TODO: There is no endpoint to get a single shipping carrier's information. If this turns out to be important,
    #  we can retrieve all shipping carriers periodically and then keep a record of them in the database so that we can
    #  create a relationship here
    shipping_carrier_id = Column(Integer)
    mail_class = Column(String)
    min_delivery_days = Column(Integer)
    max_delivery_days = Column(Integer)

    # relationships

    # many to one
    _shipping_profile_id = Column(Integer, ForeignKey('etsy_shipping_profile.id'))
    shipping_profile = relationship("EtsyShippingProfile", uselist=False, back_populates="destinations")

    @classmethod
    def create(cls, shipping_destination_data: Union[EtsyShippingProfileDestinationSpace, Dict[str, Any]],
               shipping_profile: EtsyShippingProfile = None
               ) -> EtsyShippingProfileDestination:
        if not isinstance(shipping_destination_data, EtsyShippingProfileDestinationSpace):
            shipping_destination_data = cls.create_namespace(shipping_destination_data)

        shipping_destination = cls(
            shipping_profile_destination_id=shipping_destination_data.shipping_profile_destination_id,
            origin_country_iso=shipping_destination_data.origin_country_iso,
            destination_country_iso=shipping_destination_data.destination_country_iso,
            destination_region=shipping_destination_data.destination_region,
            primary_cost=shipping_destination_data.primary_cost,
            primary_cost_divisor=shipping_destination_data.primary_cost_divisor,
            primary_cost_currency_code=shipping_destination_data.primary_cost_currency_code,
            secondary_cost=shipping_destination_data.secondary_cost,
            secondary_cost_divisor=shipping_destination_data.secondary_cost_divisor,
            secondary_cost_currency_code=shipping_destination_data.secondary_cost_currency_code,
            shipping_carrier_id=shipping_destination_data.shipping_carrier_id,
            mail_class=shipping_destination_data.mail_class,
            min_delivery_days=shipping_destination_data.min_delivery_days,
            max_delivery_days=shipping_destination_data.max_delivery_days
        )

        if shipping_profile is not None:
            shipping_destination.shipping_profile = shipping_profile

        return shipping_destination

    @staticmethod
    def create_namespace(shipping_destination_data: Dict[str, Any]):
        return EtsyShippingProfileDestinationSpace(shipping_destination_data)

    @staticmethod
    def get_existing(session, shipping_destination_id: int) -> Union[None, EtsyShippingProfileDestination]:
        return session.query(EtsyShippingProfileDestination).filter(
            EtsyShippingProfileDestination.shipping_profile_destination_id == int(shipping_destination_id)
        ).first()

    def update(self, shipping_destination_data: Union[EtsyShippingProfileDestinationSpace, Dict[str, Any]],
               shipping_profile: EtsyShippingProfile = None
               ):
        if not isinstance(shipping_destination_data, EtsyShippingProfileDestinationSpace):
            shipping_destination_data = self.create_namespace(shipping_destination_data)

        if self.origin_country_iso != shipping_destination_data.origin_country_iso:
            self.origin_country_iso = shipping_destination_data.origin_country_iso
        if self.destination_country_iso != shipping_destination_data.destination_country_iso:
            self.destination_country_iso = shipping_destination_data.destination_country_iso
        if self.destination_region != shipping_destination_data.destination_region:
            self.destination_region = shipping_destination_data.destination_region
        if self.primary_cost != shipping_destination_data.primary_cost:
            self.primary_cost = shipping_destination_data.primary_cost
        if self.primary_cost_divisor != shipping_destination_data.primary_cost_divisor:
            self.primary_cost_divisor = shipping_destination_data.primary_cost_divisor
        if self.primary_cost_currency_code != shipping_destination_data.primary_cost_currency_code:
            self.primary_cost_currency_code = shipping_destination_data.primary_cost_currency_code
        if self.secondary_cost != shipping_destination_data.secondary_cost:
            self.secondary_cost = shipping_destination_data.secondary_cost
        if self.secondary_cost_divisor != shipping_destination_data.secondary_cost_divisor:
            self.secondary_cost_divisor = shipping_destination_data.secondary_cost_divisor
        if self.secondary_cost_currency_code != shipping_destination_data.secondary_cost_currency_code:
            self.secondary_cost_currency_code = shipping_destination_data.secondary_cost_currency_code
        if self.shipping_carrier_id != shipping_destination_data.shipping_carrier_id:
            self.shipping_carrier_id = shipping_destination_data.shipping_carrier_id
        if self.mail_class != shipping_destination_data.mail_class:
            self.mail_class = shipping_destination_data.mail_class
        if self.min_delivery_days != shipping_destination_data.min_delivery_days:
            self.min_delivery_days = shipping_destination_data.min_delivery_days
        if self.max_delivery_days != shipping_destination_data.max_delivery_days:
            self.max_delivery_days = shipping_destination_data.max_delivery_days

        if shipping_profile is not None and self.shipping_profile != shipping_profile:
            self.shipping_profile = shipping_profile


class EtsyShippingProfileUpgrade(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getShopShippingProfileUpgrades
    """
    __tablename__ = 'etsy_shipping_profile_upgrade'
    id = Column(Integer, primary_key=True)
    upgrade_id = Column(BigInteger, unique=True)
    upgrade_name = Column(String)
    type = Column(Enum(Etsy.ShippingUpgradeType))
    rank = Column(Integer)
    language = Column(String)
    price = Column(Integer)
    price_divisor = Column(Integer)
    price_currency_code = Column(String)
    secondary_price = Column(Integer)
    secondary_price_divisor = Column(Integer)
    secondary_price_currency_code = Column(String)

    # TODO: There is no endpoint to get a single shipping carrier's information. If this turns out to be important,
    #  we can retrieve all shipping carriers periodically and then keep a record of them in the database so that we can
    #  create a relationship here
    shipping_carrier_id = Column(String)
    mail_class = Column(String)
    min_delivery_days = Column(Integer)
    max_delivery_days = Column(Integer)

    # relationships

    # many to one
    _shipping_profile_id = Column(Integer, ForeignKey('etsy_shipping_profile.id'))
    shipping_profile = relationship("EtsyShippingProfile", uselist=False, back_populates="upgrades")

    @classmethod
    def create(cls, shipping_upgrade_data: Union[EtsyShippingProfileUpgradeSpace, Dict[str, Any]],
               shipping_profile: EtsyShippingProfile = None
               ) -> EtsyShippingProfileUpgrade:
        if not isinstance(shipping_upgrade_data, EtsyShippingProfileUpgradeSpace):
            shipping_upgrade_data = cls.create_namespace(shipping_upgrade_data)

        shipping_upgrade = cls(
            upgrade_id=shipping_upgrade_data.upgrade_id,
            upgrade_name=shipping_upgrade_data.upgrade_name,
            type=shipping_upgrade_data.type,
            rank=shipping_upgrade_data.rank,
            language=shipping_upgrade_data.language,
            price=shipping_upgrade_data.price,
            price_divisor=shipping_upgrade_data.price_divisor,
            price_currency_code=shipping_upgrade_data.price_currency_code,
            secondary_price=shipping_upgrade_data.secondary_price,
            secondary_price_divisor=shipping_upgrade_data.secondary_price_divisor,
            secondary_price_currency_code=shipping_upgrade_data.secondary_price_currency_code,
            shipping_carrier_id=shipping_upgrade_data.shipping_carrier_id,
            mail_class=shipping_upgrade_data.mail_class,
            min_delivery_days=shipping_upgrade_data.min_delivery_days,
            max_delivery_days=shipping_upgrade_data.max_delivery_days
        )

        if shipping_profile is not None:
            shipping_upgrade.shipping_profile = shipping_profile

        return shipping_upgrade

    @staticmethod
    def create_namespace(shipping_upgrade_data: Dict[str, Any]):
        return EtsyShippingProfileUpgradeSpace(shipping_upgrade_data)

    @staticmethod
    def get_existing(session, shipping_upgrade_id: int) -> Union[None, EtsyShippingProfileUpgrade]:
        return session.query(EtsyShippingProfileUpgrade).filter(
            EtsyShippingProfileUpgrade.upgrade_id == int(shipping_upgrade_id)
        ).first()

    def update(self, shipping_upgrade_data: Union[EtsyShippingProfileUpgradeSpace, Dict[str, Any]],
               shipping_profile: EtsyShippingProfile = None
               ):
        if not isinstance(shipping_upgrade_data, EtsyShippingProfileUpgradeSpace):
            shipping_upgrade_data = self.create_namespace(shipping_upgrade_data)

        if self.upgrade_name != shipping_upgrade_data.upgrade_name:
            self.upgrade_name = shipping_upgrade_data.upgrade_name
        if self.type != shipping_upgrade_data.type:
            self.type = shipping_upgrade_data.type
        if self.rank != shipping_upgrade_data.rank:
            self.rank = shipping_upgrade_data.rank
        if self.language != shipping_upgrade_data.language:
            self.language = shipping_upgrade_data.language
        if self.price != shipping_upgrade_data.price:
            self.price = shipping_upgrade_data.price
        if self.price_divisor != shipping_upgrade_data.price_divisor:
            self.price_divisor = shipping_upgrade_data.price_divisor
        if self.price_currency_code != shipping_upgrade_data.price_currency_code:
            self.price_currency_code = shipping_upgrade_data.price_currency_code
        if self.secondary_price != shipping_upgrade_data.secondary_price:
            self.secondary_price = shipping_upgrade_data.secondary_price
        if self.secondary_price_divisor != shipping_upgrade_data.secondary_price_divisor:
            self.secondary_price_divisor = shipping_upgrade_data.secondary_price_divisor
        if self.secondary_price_currency_code != shipping_upgrade_data.secondary_price_currency_code:
            self.secondary_price_currency_code = shipping_upgrade_data.secondary_price_currency_code
        if self.shipping_carrier_id != shipping_upgrade_data.shipping_carrier_id:
            self.shipping_carrier_id = shipping_upgrade_data.shipping_carrier_id
        if self.mail_class != shipping_upgrade_data.mail_class:
            self.mail_class = shipping_upgrade_data.mail_class
        if self.min_delivery_days != shipping_upgrade_data.min_delivery_days:
            self.min_delivery_days = shipping_upgrade_data.min_delivery_days
        if self.max_delivery_days != shipping_upgrade_data.max_delivery_days:
            self.max_delivery_days = shipping_upgrade_data.max_delivery_days

        if shipping_profile is not None and self.shipping_profile != shipping_profile:
            self.shipping_profile = shipping_profile


class EtsyReceiptShipment(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getShopReceipt
    """
    __tablename__ = 'etsy_shipment'
    id = Column(Integer, primary_key=True)
    receipt_shipping_id = Column(BigInteger, unique=True)
    shipment_notification_timestamp = Column(DateTime)
    carrier_name = Column(String)
    tracking_code = Column(String)

    # relationships

    # many to one
    _receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
    receipt = relationship('EtsyReceipt', uselist=False, back_populates='receipt_shipments')

    @classmethod
    def create(cls, receipt_shipment_data: Union[EtsyReceiptShipmentSpace, Dict[str, Any]],
               receipt: EtsyReceipt = None) -> EtsyReceiptShipment:
        if not isinstance(receipt_shipment_data, EtsyReceiptShipmentSpace):
            receipt_shipment_data = cls.create_namespace(receipt_shipment_data)

        receipt_shipment = cls(
            receipt_shipping_id=receipt_shipment_data.receipt_shipping_id,
            shipment_notification_timestamp=receipt_shipment_data.shipment_notification_timestamp,
            carrier_name=receipt_shipment_data.carrier_name,
            tracking_code=receipt_shipment_data.tracking_code
        )

        if receipt is not None:
            receipt_shipment.receipt = receipt

        return receipt_shipment

    @staticmethod
    def create_namespace(shipment_data: Dict[str, Any]):
        return EtsyReceiptShipmentSpace(shipment_data)

    @staticmethod
    def get_existing(session, receipt_shipping_id: int) -> Union[None, EtsyReceiptShipment]:
        return session.query(EtsyReceiptShipment).filter(
            EtsyReceiptShipment.receipt_shipping_id == int(receipt_shipping_id)
        ).first()

    def update(self, receipt_shipment_data: Union[EtsyReceiptShipmentSpace, Dict[str, Any]],
               receipt: EtsyReceipt = None):
        if not isinstance(receipt_shipment_data, EtsyReceiptShipmentSpace):
            receipt_shipment_data = self.create_namespace(receipt_shipment_data)

        if self.shipment_notification_timestamp != receipt_shipment_data.shipment_notification_timestamp:
            self.shipment_notification_timestamp = receipt_shipment_data.shipment_notification_timestamp
        if self.carrier_name != receipt_shipment_data.carrier_name:
            self.carrier_name = receipt_shipment_data.carrier_name
        if self.tracking_code != receipt_shipment_data.tracking_code:
            self.tracking_code = receipt_shipment_data.tracking_code

        if receipt is not None and self.receipt != receipt:
            self.receipt = receipt


class EtsyVariation(Base):
    __tablename__ = 'etsy_variation'
    id = Column(Integer, primary_key=True)
    formatted_name = Column(String)
    formatted_value = Column(String)


class EtsyProductProperty(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getListingProperties
    """
    __tablename__ = 'etsy_product_property'
    id: Mapped[int] = mapped_column(primary_key=True)
    property_id = Column(BigInteger, unique=True)
    property_name = Column(String)
    scale_id = Column(BigInteger)
    scale_name = Column(String)

    # relationships

    # many to one
    _product_id = Column(Integer, ForeignKey('etsy_product.id'))
    product = relationship("EtsyProduct", uselist=False, back_populates='properties')

    # many to many
    transactions: Mapped[List[EtsyTransaction]] = relationship(
        secondary=transaction_product_data_association_table, back_populates="product_properties"
    )

    @classmethod
    def create(cls, property_data: Union[EtsyProductPropertySpace, Dict[str, Any]],
               product: EtsyProduct = None, transactions: List[EtsyTransaction] = None) -> EtsyProductProperty:
        if not isinstance(property_data, EtsyProductPropertySpace):
            property_data = cls.create_namespace(property_data)

        property_i = cls(
            property_id=property_data.property_id,
            property_name=property_data.property_name,
            scale_id=property_data.scale_id,
            scale_name=property_data.scale_name
        )

        if product is not None:
            property_i.product = product

        if transactions is not None:
            property_i.transactions = transactions

        return property_i

    @staticmethod
    def create_namespace(property_data: Dict[str, Any]):
        return EtsyProductPropertySpace(property_data)

    @staticmethod
    def get_existing(session, property_id: int, property_name: str) -> Union[None, EtsyProductProperty]:
        return session.query(EtsyProductProperty).filter(
            EtsyProductProperty.property_id == int(property_id)
        ).filter(
            EtsyProductProperty.property_name == property_name
        ).first()

    def update(self, property_data: Union[EtsyProductPropertySpace, Dict[str, Any]],
               transactions: List[EtsyTransaction] = None,
               overwrite_lists: bool = False):
        if not isinstance(property_data, EtsyProductPropertySpace):
            property_data = self.create_namespace(property_data)

        if self.property_name != property_data.property_name:
            self.property_name = property_data.property_name
        if self.scale_id != property_data.scale_id:
            self.scale_id = property_data.scale_id
        if self.scale_name != property_data.scale_name:
            self.scale_name = property_data.scale_name

        if transactions is not None:
            self.transactions = transactions if overwrite_lists else merge_lists(self.transactions, transactions)


class EtsyListing(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getListing
    """
    __tablename__ = 'etsy_listing'
    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id = Column(BigInteger, unique=True)
    title = Column(String)
    description = Column(String)
    state = Column(Enum(Etsy.ListingState))
    creation_timestamp = Column(DateTime)
    created_timestamp = Column(DateTime)
    ending_timestamp = Column(DateTime)
    original_creation_timestamp = Column(DateTime)
    last_modified_timestamp = Column(DateTime)
    updated_timestamp = Column(DateTime)
    state_timestamp = Column(DateTime)
    quantity = Column(Integer)
    featured_rank = Column(Integer)
    url = Column(String)
    num_favorers = Column(Integer)
    non_taxable = Column(Boolean)
    is_taxable = Column(Boolean)
    is_customizable = Column(Boolean)
    is_personalizable = Column(Boolean)
    personalization_is_required = Column(Boolean)
    personalization_char_count_max = Column(Integer)
    personalization_instructions = Column(String)
    listing_type = Column(Enum(Etsy.ListingType))
    tags = Column(String)  # Array
    materials = Column(String)  # Array
    processing_min = Column(Integer)
    processing_max = Column(Integer)
    who_made = Column(String)
    when_made = Column(String)
    is_supply = Column(Boolean)
    item_weight = Column(Float)
    item_weight_unit = Column(Enum(Etsy.ItemWeightUnit))
    item_length = Column(Float)
    item_width = Column(Float)
    item_height = Column(Float)
    item_dimensions_unit = Column(Enum(Etsy.ItemDimensionsUnit))
    is_private = Column(Boolean)
    style = Column(String)  # Array
    file_data = Column(String)
    has_variations = Column(Boolean)
    should_auto_renew = Column(Boolean)
    language = Column(String)
    price = Column(Integer)
    price_divisor = Column(Integer)
    price_currency_code = Column(String)
    taxonomy_id = Column(Integer)
    skus = Column(String)
    views = Column(Integer)

    # relationships

    # many to one
    _shipping_profile_id = Column(Integer, ForeignKey("etsy_shipping_profile.id"))
    shipping_profile = relationship("EtsyShippingProfile", uselist=False, back_populates="listings")
    _seller_id = Column(Integer, ForeignKey("etsy_seller.id"))
    seller = relationship("EtsySeller", uselist=False, back_populates="listings")
    _shop_id = Column(Integer, ForeignKey("etsy_shop.id"))
    shop = relationship("EtsyShop", uselist=False, back_populates="listings")
    _shop_section_id = Column(Integer, ForeignKey('etsy_shop_section.id'))
    shop_section = relationship("EtsyShopSection", uselist=False, back_populates="listings")
    _return_policy_id = Column(Integer, ForeignKey('etsy_return_policy.id'))
    return_policy = relationship("EtsyReturnPolicy", uselist=False, back_populates="listings")

    # many to many
    products: Mapped[List[EtsyProduct]] = relationship(
        secondary=listing_product_association_table, back_populates="listings"
    )
    production_partners: Mapped[List[EtsyProductionPartner]] = relationship(
        secondary=listing_production_partner_association_table, back_populates="listings"
    )

    @classmethod
    def create(cls, listing_data: Union[EtsyListingSpace, Dict[str, Any]],
               shipping_profile: EtsyShippingProfile = None,
               seller: EtsySeller = None,
               shop: EtsyShop = None,
               shop_section: EtsyShopSection = None,
               return_policy: EtsyReturnPolicy = None,
               products: List[EtsyProduct] = None,
               production_partners: List[EtsyProductionPartner] = None
               ) -> EtsyListing:
        if not isinstance(listing_data, EtsyListingSpace):
            listing_data = cls.create_namespace(listing_data)

        listing = cls(
            listing_id=listing_data.listing_id,
            title=listing_data.title,
            description=listing_data.description,
            state=listing_data.state,
            creation_timestamp=listing_data.creation_timestamp,
            created_timestamp=listing_data.created_timestamp,
            ending_timestamp=listing_data.ending_timestamp,
            original_creation_timestamp=listing_data.original_creation_timestamp,
            last_modified_timestamp=listing_data.last_modified_timestamp,
            updated_timestamp=listing_data.updated_timestamp,
            state_timestamp=listing_data.state_timestamp,
            quantity=listing_data.quantity,
            featured_rank=listing_data.featured_rank,
            url=listing_data.url,
            num_favorers=listing_data.num_favorers,
            non_taxable=listing_data.non_taxable,
            is_taxable=listing_data.is_taxable,
            is_customizable=listing_data.is_customizable,
            is_personalizable=listing_data.is_personalizable,
            personalization_is_required=listing_data.personalization_is_required,
            personalization_char_count_max=listing_data.personalization_char_count_max,
            personalization_instructions=listing_data.personalization_instructions,
            listing_type=listing_data.listing_type,
            tags=listing_data.tags,
            materials=listing_data.materials,
            processing_min=listing_data.processing_min,
            processing_max=listing_data.processing_max,
            who_made=listing_data.who_made,
            when_made=listing_data.when_made,
            is_supply=listing_data.is_supply,
            item_weight=listing_data.item_weight,
            item_weight_unit=listing_data.item_weight_unit,
            item_length=listing_data.item_length,
            item_width=listing_data.item_width,
            item_height=listing_data.item_height,
            item_dimensions_unit=listing_data.item_dimensions_unit,
            is_private=listing_data.is_private,
            style=listing_data.style,
            file_data=listing_data.file_data,
            has_variations=listing_data.has_variations,
            should_auto_renew=listing_data.should_auto_renew,
            language=listing_data.language,
            price=listing_data.price,
            price_divisor=listing_data.price_divisor,
            price_currency_code=listing_data.price_currency_code,
            taxonomy_id=listing_data.taxonomy_id,
            skus=listing_data.skus,
            views=listing_data.views
        )

        if shipping_profile is not None:
            listing.shipping_profile = shipping_profile

        if seller is not None:
            listing.seller = seller

        if shop is not None:
            listing.shop = shop

        if shop_section is not None:
            listing.shop_section = shop_section

        if return_policy is not None:
            listing.return_policy = return_policy

        if production_partners is not None:
            listing.production_partners = production_partners

        if products is not None:
            listing.products = products

        return listing

    @staticmethod
    def create_namespace(listing_data: Dict[str, Any]) -> EtsyListingSpace:
        return EtsyListingSpace(listing_data)

    @staticmethod
    def get_existing(session, listing_id: int) -> Union[None, EtsyListing]:
        return session.query(EtsyListing).filter(
            EtsyListing.listing_id == int(listing_id)
        ).first()

    def update(self, listing_data: Union[EtsyListingSpace, Dict[str, Any]] = None,
               shipping_profile: EtsyShippingProfile = None,
               seller: EtsySeller = None,
               shop: EtsyShop = None,
               shop_section: EtsyShopSection = None,
               return_policy: EtsyReturnPolicy = None,
               products: List[EtsyProduct] = None,
               production_partners: List[EtsyProductionPartner] = None,
               overwrite_list: bool = False
               ):

        if listing_data is not None:
            if not isinstance(listing_data, EtsyListingSpace):
                listing_data = self.create_namespace(listing_data)

            if self.title != listing_data.title:
                self.title = listing_data.title
            if self.description != listing_data.description:
                self.description = listing_data.description
            if self.state != listing_data.state:
                self.state = listing_data.state
            if self.creation_timestamp != listing_data.creation_timestamp:
                self.creation_timestamp = listing_data.creation_timestamp
            if self.created_timestamp != listing_data.created_timestamp:
                self.created_timestamp = listing_data.created_timestamp
            if self.ending_timestamp != listing_data.ending_timestamp:
                self.ending_timestamp = listing_data.ending_timestamp
            if self.original_creation_timestamp != listing_data.original_creation_timestamp:
                self.original_creation_timestamp = listing_data.original_creation_timestamp
            if self.last_modified_timestamp != listing_data.last_modified_timestamp:
                self.last_modified_timestamp = listing_data.last_modified_timestamp
            if self.updated_timestamp != listing_data.updated_timestamp:
                self.updated_timestamp = listing_data.updated_timestamp
            if self.state_timestamp != listing_data.state_timestamp:
                self.state_timestamp = listing_data.state_timestamp
            if self.quantity != listing_data.quantity:
                self.quantity = listing_data.quantity
            if self.featured_rank != listing_data.featured_rank:
                self.featured_rank = listing_data.featured_rank
            if self.url != listing_data.url:
                self.url = listing_data.url
            if self.num_favorers != listing_data.num_favorers:
                self.num_favorers = listing_data.num_favorers
            if self.non_taxable != listing_data.non_taxable:
                self.non_taxable = listing_data.non_taxable
            if self.is_taxable != listing_data.is_taxable:
                self.is_taxable = listing_data.is_taxable
            if self.is_customizable != listing_data.is_customizable:
                self.is_customizable = listing_data.is_customizable
            if self.is_personalizable != listing_data.is_personalizable:
                self.is_personalizable = listing_data.is_personalizable
            if self.personalization_is_required != listing_data.personalization_is_required:
                self.personalization_is_required = listing_data.personalization_is_required
            if self.personalization_char_count_max != listing_data.personalization_char_count_max:
                self.personalization_char_count_max = listing_data.personalization_char_count_max
            if self.personalization_instructions != listing_data.personalization_instructions:
                self.personalization_instructions = listing_data.personalization_instructions
            if self.listing_type != listing_data.listing_type:
                self.listing_type = listing_data.listing_type
            if self.tags != listing_data.tags:
                self.tags = listing_data.tags
            if self.materials != listing_data.materials:
                self.materials = listing_data.materials
            if self.processing_min != listing_data.processing_min:
                self.processing_min = listing_data.processing_min
            if self.processing_max != listing_data.processing_max:
                self.processing_max = listing_data.processing_max
            if self.who_made != listing_data.who_made:
                self.who_made = listing_data.who_made
            if self.when_made != listing_data.when_made:
                self.when_made = listing_data.when_made
            if self.is_supply != listing_data.is_supply:
                self.is_supply = listing_data.is_supply
            if self.item_weight != listing_data.item_weight:
                self.item_weight = listing_data.item_weight
            if self.item_weight_unit != listing_data.item_weight_unit:
                self.item_weight_unit = listing_data.item_weight_unit
            if self.item_length != listing_data.item_length:
                self.item_length = listing_data.item_length
            if self.item_width != listing_data.item_width:
                self.item_width = listing_data.item_width
            if self.item_height != listing_data.item_height:
                self.item_height = listing_data.item_height
            if self.item_dimensions_unit != listing_data.item_dimensions_unit:
                self.item_dimensions_unit = listing_data.item_dimensions_unit
            if self.is_private != listing_data.is_private:
                self.is_private = listing_data.is_private
            if self.style != listing_data.style:
                self.style = listing_data.style
            if self.file_data != listing_data.file_data:
                self.file_data = listing_data.file_data
            if self.has_variations != listing_data.has_variations:
                self.has_variations = listing_data.has_variations
            if self.should_auto_renew != listing_data.should_auto_renew:
                self.should_auto_renew = listing_data.should_auto_renew
            if self.language != listing_data.language:
                self.language = listing_data.language
            if self.price != listing_data.price:
                self.price = listing_data.price
            if self.price_divisor != listing_data.price_divisor:
                self.price_divisor = listing_data.price_divisor
            if self.price_currency_code != listing_data.price_currency_code:
                self.price_currency_code = listing_data.price_currency_code
            if self.taxonomy_id != listing_data.taxonomy_id:
                self.taxonomy_id = listing_data.taxonomy_id
            if self.skus != listing_data.skus:
                self.skus = listing_data.skus
            if self.views != listing_data.views:
                self.views = listing_data.views

        if shipping_profile is not None and self.shipping_profile != shipping_profile:
            self.shipping_profile = shipping_profile

        if seller is not None and self.seller != seller:
            self.seller = seller

        if shop is not None and self.shop != shop:
            self.shop = shop

        if shop_section is not None and self.shop_section != shop_section:
            self.shop_section = shop_section

        if return_policy is not None and self.return_policy != return_policy:
            self.return_policy = return_policy

        if production_partners is not None:
            self.production_partners = production_partners if overwrite_list else merge_lists(self.production_partners,
                                                                                              production_partners)

        if products is not None:
            self.products = products if overwrite_list else merge_lists(self.products, products)


class EtsyReturnPolicy(Base):
    """
    https://developer.etsy.com/documentation/reference#operation/getShopReturnPolicy
    """
    __tablename__ = 'etsy_return_policy'
    id = Column(Integer, primary_key=True)
    return_policy_id = Column(BigInteger, unique=True)
    accepts_returns = Column(Boolean)
    accepts_exchanges = Column(Boolean)
    return_deadline = Column(Integer)

    # relationships

    # many to one
    _shop_id = Column(Integer, ForeignKey("etsy_shop.id"))
    shop = relationship("EtsyShop", uselist=False, back_populates="return_policies")

    # one to many
    listings = relationship("EtsyListing", back_populates="return_policy")

    @classmethod
    def create(cls, return_policy_data: Union[EtsyReturnPolicySpace, Dict[str, Any]],
               shop: EtsyShop = None,
               listings: List[EtsyListing] = None) -> EtsyReturnPolicy:
        if not isinstance(return_policy_data, EtsyReturnPolicySpace):
            return_policy_data = cls.create_namespace(return_policy_data)

        return_policy = cls(
            return_policy_id=return_policy_data.return_policy_id,
            accepts_returns=return_policy_data.accepts_returns,
            accepts_exchanges=return_policy_data.accepts_exchanges,
            return_deadline=return_policy_data.return_deadline
        )

        if shop is not None:
            return_policy.shop = shop

        if listings is not None:
            return_policy.listings = listings

        return return_policy

    @staticmethod
    def create_namespace(return_policy_data: Dict[str, Any]):
        return EtsyReturnPolicy(return_policy_data)

    @staticmethod
    def get_existing(session, return_policy_id: int) -> Union[None, EtsyReturnPolicy]:
        return session.query(EtsyReturnPolicy).filter(
            EtsyReturnPolicy.return_policy_id == int(return_policy_id)
        ).first()

    def update(self, return_policy_data: Union[EtsyReturnPolicySpace, Dict[str, Any]],
               shop: EtsyShop = None,
               listings: List[EtsyListing] = None,
               overwrite_list: bool = False):
        if not isinstance(return_policy_data, EtsyReturnPolicySpace):
            return_policy_data = self.create_namespace(return_policy_data)

        if self.accepts_returns != return_policy_data.accepts_returns:
            self.accepts_returns = return_policy_data.accepts_returns
        if self.accepts_returns != return_policy_data.accepts_returns:
            self.accepts_exchanges = return_policy_data.accepts_exchanges
        if self.return_deadline != return_policy_data.return_deadline:
            self.return_deadline = return_policy_data.return_deadline

        if shop is not None and self.shop != shop:
            self.shop = shop

        if listings is not None:
            self.listings = listings if overwrite_list else merge_lists(self.listings, listings)


class EtsyShopSection(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getShopSection
    """
    __tablename__ = 'etsy_shop_section'
    id = Column(Integer, primary_key=True)
    shop_section_id = Column(BigInteger, unique=True)
    title = Column(String)
    rank = Column(Integer)
    active_listing_count = Column(Integer)

    # relationships

    # many to one
    _seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates="shop_sections")
    _shop_id = Column(Integer, ForeignKey('etsy_shop.id'))
    shop = relationship("EtsyShop", uselist=False, back_populates="shop_sections")

    # one to many
    listings = relationship("EtsyListing", back_populates="shop_section")

    @classmethod
    def create(cls, shop_section_data: Union[EtsyShopSectionSpace, Dict[str, Any]],
               seller: EtsySeller = None, shop: EtsyShop = None,
               listings: List[EtsyListing] = None) -> EtsyShopSection:
        if not isinstance(shop_section_data, EtsyShopSectionSpace):
            shop_section_data = cls.create_namespace(shop_section_data)

        shop_section = cls(
            shop_section_id=shop_section_data.shop_section_id,
            title=shop_section_data.title,
            rank=shop_section_data.rank,
            active_listing_count=shop_section_data.active_listing_count
        )

        if seller is not None:
            shop_section.seller = seller

        if shop is not None:
            shop_section.shop = shop

        if listings is not None:
            shop_section.listings = listings

        return shop_section

    @staticmethod
    def create_namespace(shop_section_data: Dict[str, Any]):
        return EtsyShopSection(shop_section_data)

    @staticmethod
    def get_existing(session, shop_section_id: int) -> Union[None, EtsyShopSection]:
        return session.query(EtsyShopSection).filter(
            EtsyShopSection.shop_section_id == int(shop_section_id)
        ).first()

    def update(self, shop_section_data: Union[EtsyShopSectionSpace, Dict[str, Any]],
               seller: EtsySeller = None, shop: EtsyShop = None,
               listings: List[EtsyListing] = None,
               overwrite_list: bool = False):
        if not isinstance(shop_section_data, EtsyShopSectionSpace):
            shop_section_data = self.create_namespace(shop_section_data)

        if self.title != shop_section_data.title:
            self.title = shop_section_data.title
        if self.rank != shop_section_data.rank:
            self.rank = shop_section_data.rank
        if self.active_listing_count != shop_section_data.active_listing_count:
            self.active_listing_count = shop_section_data.active_listing_count

        if seller is not None and self.seller != seller:
            self.seller = seller

        if shop is not None and self.shop != shop:
            self.shop = shop

        if listings is not None:
            self.listings = listings if overwrite_list else merge_lists(self.listings, listings)


class EtsyProductionPartner(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getShopProductionPartners
    """
    __tablename__ = 'etsy_production_partner'
    id = Column(Integer, primary_key=True)
    production_partner_id = Column(BigInteger, unique=True)
    partner_name = Column(String)
    location = Column(String)

    # relationships

    # many to many
    listings: Mapped[List[EtsyListing]] = relationship(
        secondary=listing_production_partner_association_table, back_populates="production_partners"
    )

    @classmethod
    def create(cls, production_partner_data: Union[EtsyProductionPartnerSpace, Dict[str, Any]],
               listings: List[EtsyListing] = None) -> EtsyProductionPartner:
        if not isinstance(production_partner_data, EtsyProductionPartnerSpace):
            production_partner_data = cls.create_namespace(production_partner_data)

        production_partner = cls(
            production_partner_id=production_partner_data.production_partner_id,
            partner_name=production_partner_data.partner_name,
            location=production_partner_data.location
        )

        if listings is not None:
            production_partner.listings = listings

        return production_partner

    @staticmethod
    def create_namespace(production_partner_data: Dict[str, Any]):
        return EtsyProductionPartnerSpace(production_partner_data)

    @staticmethod
    def get_existing(session, production_partner_id: int) -> Union[None, EtsyProductionPartner]:
        return session.query(EtsyProductionPartner).filter(
            EtsyProductionPartner.production_partner_id == int(production_partner_id)
        ).first()

    def update(self, production_partner_data: Union[EtsyProductionPartnerSpace, Dict[str, Any]],
               listings: List[EtsyListing] = None,
               overwrite_list: bool = False):
        if not isinstance(production_partner_data, EtsyProductionPartnerSpace):
            production_partner_data = self.create_namespace(production_partner_data)

        if self.partner_name != production_partner_data.partner_name:
            self.partner_name = production_partner_data.partner_name
        if self.location != production_partner_data.location:
            self.location = production_partner_data.location

        if listings is not None:
            self.listings = listings if overwrite_list else merge_lists(self.listings, listings)


class EtsyShop(Base):
    """
    https://developer.etsy.com/documentation/reference#operation/getShop
    """
    __tablename__ = 'etsy_shop'
    id = Column(Integer, primary_key=True)
    shop_id = Column(BigInteger, unique=True)
    shop_name = Column(String)
    create_date = Column(DateTime)
    title = Column(String)
    announcement = Column(String)
    currency_code = Column(String)
    is_vacation = Column(Boolean)
    vacation_message = Column(String)
    sale_message = Column(String)
    digital_sale_message = Column(String)
    update_date = Column(DateTime)
    updated_timestamp = Column(DateTime)
    listing_active_count = Column(Integer)
    digital_listing_count = Column(Integer)
    login_name = Column(String)
    accepts_custom_requests = Column(Boolean)
    policy_welcome = Column(String)
    policy_payment = Column(String)
    policy_shipping = Column(String)
    policy_refunds = Column(String)
    policy_additional = Column(String)
    policy_seller_info = Column(String)
    policy_update_date = Column(DateTime)
    policy_has_private_receipt_info = Column(Boolean)
    has_unstructured_policies = Column(Boolean)
    policy_privacy = Column(String)
    vacation_autoreply = Column(String)
    url = Column(String)
    image_url_760x100 = Column(String)
    num_favorers = Column(Integer)
    languages = Column(String)  # Array
    icon_url_fullxfull = Column(String)
    is_using_structured_policies = Column(Boolean)
    has_onboarded_structured_policies = Column(Boolean)
    include_dispute_form_link = Column(Boolean)
    is_etsy_payments_onboarded = Column(Boolean)
    is_calculated_eligible = Column(Boolean)
    is_opted_into_buyer_promise = Column(Boolean)
    is_shop_us_based = Column(Boolean)
    transaction_sold_count = Column(Integer)
    shipping_from_country_iso = Column(String)
    shop_location_country_iso = Column(String)
    review_count = Column(Integer)
    review_average = Column(Float)

    # relationships

    # many to one
    _seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates="shops")

    # one to many
    listings = relationship("EtsyListing", back_populates="shop", cascade="all, delete, delete-orphan")
    return_policies = relationship("EtsyReturnPolicy", back_populates="shop", cascade="all, delete, delete-orphan")
    shop_sections = relationship("EtsyShopSection", back_populates="shop", cascade="all, delete, delete-orphan")

    @classmethod
    def create(cls, shop_data: Union[EtsyShopSpace, Dict[str, Any]],
               seller: EtsySeller = None,
               listings: List[EtsyListing] = None,
               return_policies: List[EtsyReturnPolicy] = None,
               shop_sections: List[EtsyShopSection] = None) -> EtsyShop:
        if not isinstance(shop_data, EtsyShopSpace):
            shop_data = cls.create_namespace(shop_data)

        shop = cls(
            shop_id=shop_data.shop_id,
            shop_name=shop_data.shop_name,
            create_date=shop_data.create_date,
            title=shop_data.title,
            announcement=shop_data.announcement,
            currency_code=shop_data.currency_code,
            is_vacation=shop_data.is_vacation,
            vacation_message=shop_data.vacation_message,
            sale_message=shop_data.sale_message,
            digital_sale_message=shop_data.digital_sale_message,
            update_date=shop_data.update_date,
            updated_timestamp=shop_data.updated_timestamp,
            listing_active_count=shop_data.listing_active_count,
            digital_listing_count=shop_data.digital_listing_count,
            login_name=shop_data.login_name,
            accepts_custom_requests=shop_data.accepts_custom_requests,
            policy_welcome=shop_data.policy_welcome,
            policy_payment=shop_data.policy_payment,
            policy_shipping=shop_data.policy_shipping,
            policy_refunds=shop_data.policy_refunds,
            policy_additional=shop_data.policy_additional,
            policy_seller_info=shop_data.policy_seller_info,
            policy_update_date=shop_data.policy_update_date,
            policy_has_private_receipt_info=shop_data.policy_has_private_receipt_info,
            has_unstructured_policies=shop_data.has_unstructured_policies,
            policy_privacy=shop_data.policy_privacy,
            vacation_autoreply=shop_data.vacation_autoreply,
            url=shop_data.url,
            image_url_760x100=shop_data.image_url_760x100,
            num_favorers=shop_data.num_favorers,
            languages=shop_data.languages,
            icon_url_fullxfull=shop_data.icon_url_fullxfull,
            is_using_structured_policies=shop_data.is_using_structured_policies,
            has_onboarded_structured_policies=shop_data.has_onboarded_structured_policies,
            include_dispute_form_link=shop_data.include_dispute_form_link,
            is_etsy_payments_onboarded=shop_data.is_etsy_payments_onboarded,
            is_calculated_eligible=shop_data.is_calculated_eligible,
            is_opted_into_buyer_promise=shop_data.is_opted_into_buyer_promise,
            is_shop_us_based=shop_data.is_shop_us_based,
            transaction_sold_count=shop_data.transaction_sold_count,
            shipping_from_country_iso=shop_data.shipping_from_country_iso,
            shop_location_country_iso=shop_data.shop_location_country_iso,
            review_count=shop_data.review_count,
            review_average=shop_data.review_average
        )

        if seller is not None:
            shop.seller = seller

        if listings is not None:
            shop.listings = listings

        if return_policies is not None:
            shop.return_policies = return_policies

        if shop_sections is not None:
            shop.shop_sections = shop_sections

        return shop

    @staticmethod
    def create_namespace(shop_data: Dict[str, Any]) -> EtsyShopSpace:
        return EtsyShopSpace(shop_data)

    @staticmethod
    def get_existing(session, shop_id: int) -> Union[None, EtsyShop]:
        return session.query(EtsyShop).filter(
            EtsyShop.shop_id == int(shop_id)
        ).first()

    def update(self, shop_data: Union[EtsyShopSpace, Dict[str, Any]],
               seller: EtsySeller = None,
               listings: List[EtsyListing] = None,
               return_policies: List[EtsyReturnPolicy] = None,
               shop_sections: List[EtsyShopSection] = None,
               overwrite_list: bool = False
               ):
        if not isinstance(shop_data, EtsyShopSpace):
            shop_data = self.create_namespace(shop_data)

        if self.shop_name != shop_data.shop_name:
            self.shop_name = shop_data.shop_name
        if self.create_date != shop_data.create_date:
            self.create_date = shop_data.create_date
        if self.title != shop_data.title:
            self.title = shop_data.title
        if self.announcement != shop_data.announcement:
            self.announcement = shop_data.announcement
        if self.currency_code != shop_data.currency_code:
            self.currency_code = shop_data.currency_code
        if self.is_vacation != shop_data.is_vacation:
            self.is_vacation = shop_data.is_vacation
        if self.vacation_message != shop_data.vacation_message:
            self.vacation_message = shop_data.vacation_message
        if self.sale_message != shop_data.sale_message:
            self.sale_message = shop_data.sale_message
        if self.digital_sale_message != shop_data.digital_sale_message:
            self.digital_sale_message = shop_data.digital_sale_message
        if self.update_date != shop_data.update_date:
            self.update_date = shop_data.update_date
        if self.updated_timestamp != shop_data.updated_timestamp:
            self.updated_timestamp = shop_data.updated_timestamp
        if self.listing_active_count != shop_data.listing_active_count:
            self.listing_active_count = shop_data.listing_active_count
        if self.digital_listing_count != shop_data.digital_listing_count:
            self.digital_listing_count = shop_data.digital_listing_count
        if self.login_name != shop_data.login_name:
            self.login_name = shop_data.login_name
        if self.accepts_custom_requests != shop_data.accepts_custom_requests:
            self.accepts_custom_requests = shop_data.accepts_custom_requests
        if self.policy_welcome != shop_data.policy_welcome:
            self.policy_welcome = shop_data.policy_welcome
        if self.policy_payment != shop_data.policy_payment:
            self.policy_payment = shop_data.policy_payment
        if self.policy_shipping != shop_data.policy_shipping:
            self.policy_shipping = shop_data.policy_shipping
        if self.policy_refunds != shop_data.policy_refunds:
            self.policy_refunds = shop_data.policy_refunds
        if self.policy_additional != shop_data.policy_additional:
            self.policy_additional = shop_data.policy_additional
        if self.policy_seller_info != shop_data.policy_seller_info:
            self.policy_seller_info = shop_data.policy_seller_info
        if self.policy_update_date != shop_data.policy_update_date:
            self.policy_update_date = shop_data.policy_update_date
        if self.policy_has_private_receipt_info != shop_data.policy_has_private_receipt_info:
            self.policy_has_private_receipt_info = shop_data.policy_has_private_receipt_info
        if self.has_unstructured_policies != shop_data.has_unstructured_policies:
            self.has_unstructured_policies = shop_data.has_unstructured_policies
        if self.policy_privacy != shop_data.policy_privacy:
            self.policy_privacy = shop_data.policy_privacy
        if self.vacation_autoreply != shop_data.vacation_autoreply:
            self.vacation_autoreply = shop_data.vacation_autoreply
        if self.url != shop_data.url:
            self.url = shop_data.url
        if self.image_url_760x100 != shop_data.image_url_760x100:
            self.image_url_760x100 = shop_data.image_url_760x100
        if self.num_favorers != shop_data.num_favorers:
            self.num_favorers = shop_data.num_favorers
        if self.languages != shop_data.languages:
            self.languages = shop_data.languages
        if self.icon_url_fullxfull != shop_data.icon_url_fullxfull:
            self.icon_url_fullxfull = shop_data.icon_url_fullxfull
        if self.is_using_structured_policies != shop_data.is_using_structured_policies:
            self.is_using_structured_policies = shop_data.is_using_structured_policies
        if self.has_onboarded_structured_policies != shop_data.has_onboarded_structured_policies:
            self.has_onboarded_structured_policies = shop_data.has_onboarded_structured_policies
        if self.include_dispute_form_link != shop_data.include_dispute_form_link:
            self.include_dispute_form_link = shop_data.include_dispute_form_link
        if self.is_etsy_payments_onboarded != shop_data.is_etsy_payments_onboarded:
            self.is_etsy_payments_onboarded = shop_data.is_etsy_payments_onboarded
        if self.is_calculated_eligible != shop_data.is_calculated_eligible:
            self.is_calculated_eligible = shop_data.is_calculated_eligible
        if self.is_opted_into_buyer_promise != shop_data.is_opted_into_buyer_promise:
            self.is_opted_into_buyer_promise = shop_data.is_opted_into_buyer_promise
        if self.is_shop_us_based != shop_data.is_shop_us_based:
            self.is_shop_us_based = shop_data.is_shop_us_based
        if self.transaction_sold_count != shop_data.transaction_sold_count:
            self.transaction_sold_count = shop_data.transaction_sold_count
        if self.shipping_from_country_iso != shop_data.shipping_from_country_iso:
            self.shipping_from_country_iso = shop_data.shipping_from_country_iso
        if self.shop_location_country_iso != shop_data.shop_location_country_iso:
            self.shop_location_country_iso = shop_data.shop_location_country_iso
        if self.review_count != shop_data.review_count:
            self.review_count = shop_data.review_count
        if self.review_average != shop_data.review_average:
            self.review_average = shop_data.review_average

        if seller is not None and self.seller != seller:
            self.seller = seller

        if listings is not None:
            self.listings = listings if overwrite_list else merge_lists(self.listings, listings)

        if return_policies is not None:
            self.return_policies = return_policies if overwrite_list else merge_lists(self.return_policies,
                                                                                      return_policies)

        if shop_sections is not None:
            self.shop_sections = shop_sections if overwrite_list else merge_lists(self.shop_sections, shop_sections)


class EtsyOffering(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getListingOffering
    """
    __tablename__ = 'etsy_offering'
    id = Column(Integer, primary_key=True)
    offering_id = Column(BigInteger, unique=True)
    quantity = Column(Integer)
    is_enabled = Column(Boolean)
    is_deleted = Column(Boolean)
    price = Column(Integer)
    price_divisor = Column(Integer)
    price_currency_code = Column(String)

    # relationships

    # many to one
    _product_id = Column(Integer, ForeignKey('etsy_product.id'))
    product = relationship("EtsyProduct", uselist=False, back_populates='offerings')

    @classmethod
    def create(cls, offering_data: Union[EtsyOfferingSpace, Dict[str, Any]],
               product: EtsyProduct = None) -> EtsyOffering:
        if not isinstance(offering_data, EtsyOfferingSpace):
            offering_data = cls.create_namespace(offering_data)

        offering = cls(
            offering_id=offering_data.offering_id,
            quantity=offering_data.quantity,
            is_enabled=offering_data.is_enabled,
            is_deleted=offering_data.is_deleted,
            price=offering_data.price,
            price_divisor=offering_data.price_divisor,
            price_currency_code=offering_data.price_currency_code
        )

        if product is not None:
            offering.product = product

        return offering

    @staticmethod
    def create_namespace(offering_data: Dict[str, Any]):
        return EtsyOfferingSpace(offering_data)

    @staticmethod
    def get_existing(session, offering_id: int) -> Union[None, EtsyOffering]:
        return session.query(EtsyOffering).filter(
            EtsyOffering.offering_id == int(offering_id)
        ).first()

    def update(self, offering_data: Union[EtsyOfferingSpace, Dict[str, Any]],
               product: EtsyProduct = None):
        if not isinstance(offering_data, EtsyOfferingSpace):
            offering_data = self.create_namespace(offering_data)

        if self.quantity != offering_data.quantity:
            self.quantity = offering_data.quantity
        if self.is_enabled != offering_data.is_enabled:
            self.is_enabled = offering_data.is_enabled
        if self.is_deleted != offering_data.is_deleted:
            self.is_deleted = offering_data.is_deleted
        if self.price != offering_data.price:
            self.price = offering_data.price
        if self.price_divisor != offering_data.price_divisor:
            self.price_divisor = offering_data.price_divisor
        if self.price_currency_code != offering_data.price_currency_code:
            self.price_currency_code = offering_data.price_currency_code

        if product is not None and self.product != product:
            self.product = product


class EtsyRefund(Base):
    __tablename__ = 'etsy_refund'
    id = Column(Integer, primary_key=True)
    amount = Column(Float)
    amount_divisor = Column(Integer)
    amount_currency_code = Column(String)
    created_timestamp = Column(DateTime)
    reason = Column(String)
    note_from_issuer = Column(String)
    status = Column(String)

    # relationships

    # many to one
    _receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
    receipt = relationship("EtsyReceipt", uselist=False, back_populates='refunds')

    @classmethod
    def create(cls, refund_data: Union[EtsyRefundSpace, Dict[str, Any]],
               receipt: EtsyReceipt = None) -> EtsyRefund:
        if not isinstance(refund_data, EtsyRefundSpace):
            refund_data = cls.create_namespace(refund_data)

        refund = cls(
            amount=refund_data.amount,
            amount_divisor=refund_data.amount_divisor,
            amount_currency_code=refund_data.amount_currency_code,
            created_timestamp=refund_data.created_timestamp,
            reason=refund_data.reason,
            note_from_issuer=refund_data.note_from_issuer,
            status=refund_data.status
        )

        if receipt is not None:
            refund.receipt = receipt

        return receipt

    @staticmethod
    def create_namespace(receipt_data: Dict[str, Any]):
        return EtsyReceiptSpace(receipt_data)


class ProdigiOrder(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#orders
    """
    __tablename__ = 'prodigi_order'
    id = Column(Integer, primary_key=True)
    prodigi_id = Column(String, unique=True)
    created = Column(DateTime)
    last_updated = Column(DateTime)
    callback_url = Column(String)
    merchant_reference = Column(String)
    shipping_method = Column(Enum(Prodigi.ShippingMethod))
    idempotency_key = Column(String)

    # relationships

    # one to many
    charges = relationship("ProdigiCharge", back_populates="order", cascade="all, delete, delete-orphan")
    shipments = relationship("ProdigiShipment", back_populates="order", cascade="all, delete, delete-orphan")
    items = relationship("ProdigiItem", back_populates="order", cascade="all, delete, delete-orphan")

    # many to one
    _recipient_id = Column(Integer, ForeignKey('prodigi_recipient.id'))
    recipient = relationship("ProdigiRecipient", uselist=False, back_populates="orders")
    _etsy_receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
    etsy_receipt = relationship("EtsyReceipt", uselist=False, back_populates="prodigi_orders")

    # one to one
    status = relationship("ProdigiStatus", uselist=False, back_populates='order', cascade="all, delete, delete-orphan")
    packing_slip = relationship("ProdigiPackingSlip", uselist=False, back_populates="order",
                                cascade="all, delete, delete-orphan")

    @classmethod
    def create(cls, order_data: Union[ProdigiOrderSpace, Dict[str, Any]],
               status: ProdigiStatus = None,
               charges: List[ProdigiCharge] = None,
               shipments: List[ProdigiShipment] = None,
               recipient: ProdigiRecipient = None,
               items: List[ProdigiItem] = None,
               packing_slip: ProdigiPackingSlip = None,
               etsy_receipt: EtsyReceipt = None
               ) -> ProdigiOrder:
        if not isinstance(order_data, ProdigiOrderSpace):
            order_data = cls.create_namespace(order_data)

        order = cls(
            prodigi_id=order_data.prodigi_id,
            created=order_data.created,
            last_updated=order_data.last_updated,
            callback_url=order_data.callback_url,
            merchant_reference=order_data.merchant_reference,
            shipping_method=order_data.shipping_method,
            idempotency_key=order_data.idempotency_key
        )

        if status is not None:
            order.status = status

        if charges is not None:
            order.charges = charges

        if shipments is not None:
            order.shipments = shipments

        if recipient is not None:
            order.recipient = recipient

        if items is not None:
            order.items = items

        if packing_slip is not None:
            order.packing_slip = packing_slip

        if etsy_receipt is not None:
            order.etsy_receipt = etsy_receipt

        return order

    @staticmethod
    def create_namespace(order_data: Dict[str, Any]) -> ProdigiOrderSpace:
        return ProdigiOrderSpace(order_data)

    @staticmethod
    def get_existing(session, prodigi_id: str) -> Union[ProdigiOrder, None]:
        return session.query(ProdigiOrder).filter(ProdigiOrder.prodigi_id == prodigi_id).first()

    def update(self, order_data: Union[ProdigiOrderSpace, Dict[str, Any]],
               status: ProdigiStatus = None,
               charges: List[ProdigiCharge] = None,
               shipments: List[ProdigiShipment] = None,
               recipient: ProdigiRecipient = None,
               items: List[ProdigiItem] = None,
               packing_slip: ProdigiPackingSlip = None,
               etsy_receipt: EtsyReceipt = None,
               overwrite_list: bool = False
               ):
        if not isinstance(order_data, ProdigiOrderSpace):
            order_data = self.create_namespace(order_data)

            if self.last_updated != order_data.last_updated:
                self.last_updated = order_data.last_updated
            if self.callback_url != order_data.callback_url:
                self.callback_url = order_data.callback_url
            if self.merchant_reference != order_data.merchant_reference:
                self.merchant_reference = order_data.merchant_reference
            if self.shipping_method != order_data.shipping_method:
                self.shipping_method = order_data.shipping_method
            if self.idempotency_key != order_data.idempotency_key:
                self.idempotency_key = order_data.idempotency_key

        # relationships
        if status is not None and self.status != status:
            self.status = status

        if recipient is not None and self.recipient != recipient:
            self.recipient = recipient

        if packing_slip is not None and self.packing_slip != packing_slip:
            self.packing_slip = packing_slip

        if etsy_receipt is not None and self.etsy_receipt != etsy_receipt:
            self.etsy_receipt = etsy_receipt

        if charges is not None:
            self.charges = charges if overwrite_list else merge_lists(self.charges, charges)

        if shipments is not None:
            self.shipments = shipments if overwrite_list else merge_lists(self.shipments, shipments)

        if items is not None:
            self.items = items if overwrite_list else merge_lists(self.items, items)


class ProdigiShipmentDetail(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#update-shipping-method
    """
    __tablename__ = 'prodigi_shipment_detail'
    id = Column(Integer, primary_key=True)
    shipment_id = Column(String)
    successful = Column(Boolean)
    error_code = Column(Enum(Prodigi.ShipmentUpdateErrorCode))
    description = Column(String)

    # relationships

    # many to one
    _shipment_id = Column(Integer, ForeignKey('prodigi_shipment.id'))
    shipment = relationship("ProdigiShipment", uselist=False, back_populates="shipment_details")

    @classmethod
    def create(cls, shipment_detail_data: Union[ProdigiShipmentDetail, Dict[str, Any]],
               shipment: ProdigiShipment = None) -> ProdigiShipmentDetail:
        if not isinstance(shipment_detail_data, ProdigiShipmentDetailSpace):
            shipment_detail_data = cls.create_namespace(shipment_detail_data)

        shipment_detail = cls(
            shipment_id=shipment_detail_data.shipment_id,
            successful=shipment_detail_data.successful,
            error_code=shipment_detail_data.error_code,
            description=shipment_detail_data.description
        )

        if shipment is not None:
            shipment_detail.shipment = shipment

        return shipment_detail

    @staticmethod
    def create_namespace(shipment_detail_data: Dict[str, Any]) -> ProdigiShipmentDetailSpace:
        return ProdigiShipmentDetailSpace(shipment_detail_data)

    def get_existing(self, session, shipment_detail_data: Union[ProdigiShipmentDetail, Dict[str, Any]]
                     ) -> Union[ProdigiShipmentDetail, None]:
        if not isinstance(shipment_detail_data, ProdigiShipmentDetailSpace):
            shipment_detail_data = self.create_namespace(shipment_detail_data)
        return session.query(ProdigiShipmentDetail).filter(
            ProdigiShipmentDetail.shipment_id == shipment_detail_data.shipment_id
        ).filter(
            ProdigiShipmentDetail.successful == shipment_detail_data.successful
        ).filter(
            ProdigiShipmentDetail.error_code == shipment_detail_data.error_code
        ).filter(
            ProdigiShipmentDetail.description == shipment_detail_data.description
        ).first()

    def update(self, shipment_detail_data: Union[ProdigiShipmentDetail, Dict[str, Any]],
               shipment: ProdigiShipment = None):
        if not isinstance(shipment_detail_data, ProdigiShipmentDetailSpace):
            shipment_detail_data = self.create_namespace(shipment_detail_data)

        if self.shipment_id != shipment_detail_data.shipment_id:
            self.shipment_id = shipment_detail_data.shipment_id
        if self.successful != shipment_detail_data.successful:
            self.successful = shipment_detail_data.successful
        if self.error_code != shipment_detail_data.error_code:
            self.error_code = shipment_detail_data.error_code
        if self.description != shipment_detail_data.description:
            self.description = shipment_detail_data.description

        if shipment is not None and self.shipment != shipment:
            self.shipment = shipment


class ProdigiPackingSlip(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-packing-slip
    """
    __tablename__ = 'prodigi_packing_slip'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    status = Column(String)

    # relationships

    # one to one
    _order_id = Column(Integer, ForeignKey('prodigi_order.id'))
    order = relationship("ProdigiOrder", uselist=False, back_populates="packing_slip")

    @classmethod
    def create(cls, packing_slip_data: Union[ProdigiPackingSlipSpace, Dict[str, Any]],
               order: ProdigiOrder = None) -> ProdigiPackingSlip:
        if not isinstance(packing_slip_data, ProdigiPackingSlipSpace):
            packing_slip_data = cls.create_namespace(packing_slip_data)

        packing_slip = cls(
            url=packing_slip_data.url,
            status=packing_slip_data.status
        )

        if order is not None:
            packing_slip.order = order

        return order

    @staticmethod
    def create_namespace(packing_slip_data: Dict[str, Any]) -> ProdigiPackingSlipSpace:
        return ProdigiPackingSlipSpace(packing_slip_data)

    def update(self, packing_slip_data: Union[ProdigiPackingSlipSpace, Dict[str, Any]],
               order: ProdigiOrder = None):
        if not isinstance(packing_slip_data, ProdigiPackingSlipSpace):
            packing_slip_data = self.create_namespace(packing_slip_data)

        if self.url != packing_slip_data.url:
            self.url = packing_slip_data.url
        if self.status != packing_slip_data.status:
            self.status = packing_slip_data.status

        if order is not None and self.order != order:
            self.order = order


class ProdigiItem(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-item
    """
    __tablename__ = 'prodigi_item'
    id = Column(Integer, primary_key=True)
    prodigi_id = Column(String, unique=True)
    merchant_reference = Column(String)
    sku = Column(String)
    copies = Column(Integer)
    sizing = Column(Enum(Prodigi.Sizing))

    # relationships

    # many to one
    _order_id = Column(Integer, ForeignKey('prodigi_order.id'))
    order = relationship("ProdigiOrder", uselist=False, back_populates='items')

    # one to one
    recipient_cost = relationship("ProdigiCost", uselist=False, back_populates='item',
                                  cascade="all, delete, delete-orphan")

    # many to many
    assets: Mapped[List[ProdigiAsset]] = relationship(secondary=item_asset_association_table, back_populates='items')

    @classmethod
    def create(cls, item_data: Union[ProdigiItemSpace, Dict[str, Any]],
               order: ProdigiOrder = None,
               recipient_cost: ProdigiCost = None,
               assets: List[ProdigiAsset] = None
               ) -> ProdigiItem:
        if not isinstance(item_data, ProdigiItemSpace):
            item_data = cls.create_namespace(item_data)

        item = cls(
            prodigi_id=item_data.prodigi_id,
            merchant_reference=item_data.merchant_reference,
            sku=item_data.sku,
            copies=item_data.copies,
            sizing=item_data.sizing
        )

        if order is not None:
            item.order = order

        if recipient_cost is not None:
            item.recipient_cost = recipient_cost

        if assets is not None:
            item.assets = assets

        return item

    @staticmethod
    def create_namespace(item_data: Dict[str, Any]) -> ProdigiItemSpace:
        return ProdigiItemSpace(item_data)

    @staticmethod
    def get_existing(session, prodigi_id: str) -> ProdigiItem:
        return session.query(ProdigiItem).filter(ProdigiItem.prodigi_id == prodigi_id).first()

    def update(self, item_data: Union[ProdigiItemSpace, Dict[str, Any]],
               order: ProdigiOrder = None,
               recipient_cost: ProdigiCost = None,
               assets: List[ProdigiAsset] = None,
               overwrite_list: bool = False
               ):
        if not isinstance(item_data, ProdigiItemSpace):
            item_data = self.create_namespace(item_data)

        if self.prodigi_id != item_data.prodigi_id:
            self.prodigi_id = item_data.prodigi_id
        if self.merchant_reference != item_data.merchant_reference:
            self.merchant_reference = item_data.merchant_reference
        if self.sku != item_data.sku:
            self.sku = item_data.sku
        if self.copies != item_data.copies:
            self.copies = item_data.copies
        if self.sizing != item_data.sizing:
            self.sizing = item_data.sizing

        if order is not None and self.order != order:
            self.order = order

        if recipient_cost is not None and self.recipient_cost != recipient_cost:
            self.recipient_cost = recipient_cost

        if assets is not None:
            self.assets = assets if overwrite_list else merge_lists(self.assets, assets)


class ProdigiAsset(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-asset
    """
    __tablename__ = 'prodigi_asset'
    id = Column(Integer, primary_key=True)
    print_area = Column(String)
    url = Column(String)

    # relationships

    # many to many
    items: Mapped[List[ProdigiItem]] = relationship(secondary=item_asset_association_table, back_populates='assets')

    @classmethod
    def create(cls, asset_data: Union[ProdigiAssetSpace, Dict[str, Any]],
               items: List[ProdigiItem] = None) -> ProdigiAsset:
        if not isinstance(asset_data, ProdigiAssetSpace):
            asset_data = cls.create_namespace(asset_data)

        asset = cls(
            print_area=asset_data.print_area,
            url=asset_data.url
        )

        if items is not None:
            asset.items = items

        return asset

    @staticmethod
    def create_namespace(asset_data: Dict[str, Any]) -> ProdigiAssetSpace:
        return ProdigiAssetSpace(asset_data)

    @staticmethod
    def get_existing(session, asset_data: Union[ProdigiAssetSpace, Dict[str, Any]]):
        if not isinstance(asset_data, ProdigiAssetSpace):
            asset_data = ProdigiAsset.create_namespace(asset_data)
        return session.query(ProdigiAsset).filter(
            ProdigiAsset.print_area == asset_data.print_area
        ).filter(
            ProdigiAsset.url == asset_data.url
        ).first()


class ProdigiRecipient(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-recipient
    """
    __tablename__ = 'prodigi_recipient'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    email = Column(String)
    phone_number = Column(String)

    # relationships

    # one to many
    orders = relationship("ProdigiOrder", back_populates="recipient")

    # many to many
    addresses: Mapped[List[Address]] = relationship(
        secondary=recipient_address_association_table, back_populates='prodigi_recipients')

    @classmethod
    def create(cls, recipient_data: Union[ProdigiRecipientSpace, Dict[str, Any]],
               orders: List[ProdigiOrder] = None,
               addresses: List[Address] = None,
               ) -> ProdigiRecipient:
        if not isinstance(recipient_data, ProdigiRecipientSpace):
            recipient_data = cls.create_namespace(recipient_data)

        recipient = cls(
            name=recipient_data.name,
            email=recipient_data.email,
            phone_number=recipient_data.phone_number
        )

        if orders is not None:
            recipient.orders = orders

        if addresses is not None:
            recipient.addresses = addresses

        return recipient

    @staticmethod
    def create_namespace(recipient_data: Dict[str, Any]) -> ProdigiRecipientSpace:
        return ProdigiRecipientSpace(recipient_data)

    @staticmethod
    def get_existing(session, recipient_data: Union[ProdigiRecipientSpace, Dict[str, Any]]):
        if not isinstance(recipient_data, ProdigiRecipientSpace):
            recipient_data = ProdigiRecipient.create_namespace(recipient_data)
        return session.query(ProdigiRecipient).filter(
            ProdigiRecipient.name == recipient_data.name
        ).filter(
            ProdigiRecipient.email == recipient_data.email
        ).filter(
            ProdigiRecipient.phone_number == recipient_data.phone_number
        ).first()

    def update(self, orders: List[ProdigiOrder] = None, addresses: List[Address] = None, overwrite_list: bool = False):
        if orders is not None:
            self.orders = orders if overwrite_list else merge_lists(self.orders, orders)

        if addresses is not None:
            self.addresses = addresses if overwrite_list else merge_lists(self.addresses, addresses)


class ProdigiShipment(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-shipment
    """
    __tablename__ = 'prodigi_shipment'
    id = Column(Integer, primary_key=True)
    prodigi_id = Column(String, unique=True)
    carrier_name = Column(String)
    carrier_service = Column(String)
    tracking_number = Column(String)
    tracking_url = Column(String)
    dispatch_date = Column(DateTime)

    # relationships

    # one to many
    shipment_items = relationship("ProdigiShipmentItem", back_populates='shipment',
                                  cascade="all, delete, delete-orphan")
    shipment_details = relationship("ProdigiShipmentDetail", back_populates='shipment',
                                    cascade="all, delete, delete-orphan")

    # many to one
    _order_id = Column(Integer, ForeignKey('prodigi_order.id'))
    order = relationship("ProdigiOrder", uselist=False, back_populates="shipments")

    # one to one
    fulfillment_location = relationship("ProdigiFulfillmentLocation", uselist=False, back_populates="shipment",
                                        cascade="all, delete, delete-orphan")

    @classmethod
    def create(cls, shipment_data: Union[ProdigiShipmentSpace, Dict[str, Any]],
               order: ProdigiOrder = None,
               shipment_items: List[ProdigiShipmentItem] = None,
               fulfillment_location: ProdigiFulfillmentLocation = None) -> ProdigiShipment:
        if not isinstance(shipment_data, ProdigiShipmentSpace):
            shipment_data = cls.create_namespace(shipment_data)

        shipment = cls(
            prodigi_id=shipment_data.prodigi_id,
            carrier_name=shipment_data.carrier_name,
            carrier_service=shipment_data.carrier_service,
            tracking_number=shipment_data.tracking_number,
            tracking_url=shipment_data.tracking_url,
            dispatch_date=shipment_data.dispatch_date
        )

        if order is not None:
            shipment.order = order

        if shipment_items is not None:
            shipment.shipment_items = shipment_items

        if fulfillment_location is not None:
            shipment.fulfillment_location = fulfillment_location

        return shipment

    @staticmethod
    def create_namespace(order_data: Dict[str, Any]) -> ProdigiShipmentSpace:
        return ProdigiShipmentSpace(order_data)

    @staticmethod
    def get_existing(session, prodigi_id: str) -> Union[None, ProdigiShipment]:
        return session.query(ProdigiShipment).filter(ProdigiShipment.prodigi_id == prodigi_id).first()

    def update(self, shipment_data: Union[ProdigiShipmentSpace, Dict[str, Any]],
               order: ProdigiOrder = None,
               shipment_items: List[ProdigiShipmentItem] = None,
               fulfillment_location: ProdigiFulfillmentLocation = None,
               overwrite_list: bool = False
               ):
        if not isinstance(shipment_data, ProdigiShipmentSpace):
            shipment_data = self.create_namespace(shipment_data)

        if self.carrier_name != shipment_data.carrier_name:
            self.carrier_name = shipment_data.carrier_name
        if self.carrier_service != shipment_data.carrier_service:
            self.carrier_service = shipment_data.carrier_service
        if self.tracking_number != shipment_data.tracking_number:
            self.tracking_number = shipment_data.tracking_number
        if self.tracking_url != shipment_data.tracking_url:
            self.tracking_url = shipment_data.tracking_url
        if self.dispatch_date != shipment_data.dispatch_date:
            self.dispatch_date = shipment_data.dispatch_date

        if order is not None and self.order != order:
            self.order = order

        if fulfillment_location is not None and self.fulfillment_location != fulfillment_location:
            self.fulfillment_location = fulfillment_location

        if shipment_items is not None:
            self.shipment_items = shipment_items if overwrite_list else merge_lists(self.shipment_items, shipment_items)


class ProdigiFulfillmentLocation(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-fulfillment-location
    """
    __tablename__ = 'prodigi_fulfillment_location'
    id = Column(Integer, primary_key=True)
    country_code = Column(String)
    lab_code = Column(String)

    # relationships

    # one to one
    _shipment_id = Column(Integer, ForeignKey('prodigi_shipment.id'))
    shipment = relationship("ProdigiShipment", back_populates="fulfillment_location")

    @classmethod
    def create(cls, fulfillment_location_data: Union[ProdigiFulfillmentLocationSpace, Dict[str, Any]],
               shipment: ProdigiShipment = None) -> ProdigiFulfillmentLocation:
        if not isinstance(fulfillment_location_data, ProdigiFulfillmentLocationSpace):
            fulfillment_location_data = cls.create_namespace(fulfillment_location_data)

        fulfillment_location = cls(
            country_code=fulfillment_location_data.country_code,
            lab_code=fulfillment_location_data.lab_code
        )

        if shipment is not None:
            fulfillment_location.shipment = shipment

        return fulfillment_location

    @staticmethod
    def create_namespace(fulfillment_location_data: Dict[str, Any]) -> ProdigiFulfillmentLocationSpace:
        return ProdigiFulfillmentLocationSpace(fulfillment_location_data)

    def update(self, fulfillment_location_data: Union[ProdigiFulfillmentLocationSpace, Dict[str, Any]],
               shipment: ProdigiShipment = None):
        if not isinstance(fulfillment_location_data, ProdigiFulfillmentLocationSpace):
            fulfillment_location_data = self.create_namespace(fulfillment_location_data)

        if self.country_code != fulfillment_location_data.country_code:
            self.country_code = fulfillment_location_data.country_code
        if self.lab_code != fulfillment_location_data.lab_code:
            self.lab_code = fulfillment_location_data.lab_code

        if shipment is not None and self.shipment != shipment:
            self.shipment = shipment


class ProdigiShipmentItem(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-shipment-item
    """
    __tablename__ = 'prodigi_shipment_item'
    id = Column(Integer, primary_key=True)
    item_id = Column(String, unique=True)

    # relationships

    # many to one
    _shipment_id = Column(Integer, ForeignKey('prodigi_shipment.id'))
    shipment = relationship("ProdigiShipment", uselist=False, back_populates='shipment_items')

    @classmethod
    def create(cls, shipment_item_data: Union[ProdigiShipmentItemSpace, Dict[str, Any]],
               shipment: ProdigiShipment = None) -> ProdigiShipmentItem:
        if not isinstance(shipment_item_data, ProdigiShipmentItemSpace):
            shipment_item_data = cls.create_namespace(shipment_item_data)

        shipment_item = cls(
            item_id=shipment_item_data.item_id
        )

        if shipment is not None:
            shipment_item.shipment = shipment

        return shipment_item

    @staticmethod
    def create_namespace(shipment_item_data: Dict[str, Any]) -> ProdigiShipmentItemSpace:
        return ProdigiShipmentItemSpace(shipment_item_data)

    @staticmethod
    def get_existing(session, item_id: str) -> Union[ProdigiShipmentItem, None]:
        return session.query(ProdigiShipmentItem).filter(ProdigiShipmentItem.item_id == item_id).first()

    def update(self, shipment: ProdigiShipment):

        if self.shipment != shipment:
            self.shipment = shipment


class ProdigiCharge(Base):
    __tablename__ = 'prodigi_charge'
    id = Column(Integer, primary_key=True)
    prodigi_id = Column(String, unique=True)
    prodigi_invoice_number = Column(String)

    # relationships

    # one to many
    charge_items = relationship("ProdigiChargeItem", back_populates="charge", cascade="all, delete, delete-orphan")

    # many to one
    _order_id = Column(Integer, ForeignKey('prodigi_order.id'))
    order = relationship("ProdigiOrder", uselist=False, back_populates="charges")

    # one to one
    total_cost = relationship("ProdigiCost", uselist=False, back_populates="charge",
                              cascade="all, delete, delete-orphan")

    @classmethod
    def create(cls, charge_data: Union[ProdigiChargeSpace, Dict[str, Any]],
               order: ProdigiOrder = None,
               total_cost: ProdigiCost = None,
               charge_items: List[ProdigiChargeItem] = None) -> ProdigiCharge:
        if not isinstance(charge_data, ProdigiChargeSpace):
            charge_data = cls.create_namespace(charge_data)

        charge = cls(
            prodigi_id=charge_data.prodigi_id,
            prodigi_invoice_number=charge_data.prodigi_invoice_number
        )

        if order is not None:
            charge.order = order

        if total_cost is not None:
            charge.total_cost = total_cost

        if charge_items is not None:
            charge.charge_items = charge_items

        return charge

    @staticmethod
    def create_namespace(charge_data: Dict[str, Any]) -> ProdigiChargeSpace:
        return ProdigiChargeSpace(charge_data)

    @staticmethod
    def get_existing(session, prodigi_id: str) -> Union[ProdigiCharge, None]:
        return session.query(ProdigiCharge).filter(ProdigiCharge.prodigi_id == prodigi_id).first()

    def update(self, charge_data: Union[ProdigiChargeSpace, Dict[str, Any]],
               order: ProdigiOrder = None,
               total_cost: ProdigiCost = None,
               charge_items: List[ProdigiChargeItem] = None,
               overwrite_list: bool = False
               ):
        if not isinstance(charge_data, ProdigiChargeSpace):
            charge_data = self.create_namespace(charge_data)

        if self.prodigi_invoice_number != charge_data.prodigi_invoice_number:
            self.prodigi_invoice_number = charge_data.prodigi_invoice_number

        if order is not None and self.order != order:
            self.order = order

        if total_cost is not None and self.total_cost != total_cost:
            self.total_cost = total_cost

        if charge_items is not None:
            self.charge_items = charge_items if overwrite_list else merge_lists(self.charge_items, charge_items)


class ProdigiChargeItem(Base):
    __tablename__ = 'prodigi_charge_item'
    id = Column(Integer, primary_key=True)
    prodigi_id = Column(String, unique=True)
    description = Column(String)
    item_sku = Column(String)
    shipment_id = Column(String)
    item_id = Column(String)
    merchant_item_reference = Column(String)

    # relationships

    # one to one
    cost = relationship("ProdigiCost", uselist=False, back_populates="charge_item",
                        cascade="all, delete, delete-orphan")

    # many to one
    _charge_id = Column(Integer, ForeignKey('prodigi_charge.id'))
    charge = relationship("ProdigiCharge", uselist=False, back_populates="charge_items")

    @classmethod
    def create(cls, charge_item_data: Union[ProdigiChargeItemSpace, Dict[str, Any]],
               cost: ProdigiCost = None,
               charge: ProdigiCharge = None
               ) -> ProdigiChargeItem:
        if not isinstance(charge_item_data, ProdigiChargeItemSpace):
            charge_item_data = cls.create_namespace(charge_item_data)

        charge_item = cls(
            prodigi_id=charge_item_data.prodigi_id,
            description=charge_item_data.description,
            item_sku=charge_item_data.item_sku,
            shipment_id=charge_item_data.shipment_id,
            item_id=charge_item_data.item_id,
            merchant_item_reference=charge_item_data.merchant_item_reference
        )

        if cost is not None:
            charge_item.cost = cost

        if charge is not None:
            charge_item.charge = charge

        return charge_item

    @staticmethod
    def create_namespace(charge_item_data: Dict[str, Any]) -> ProdigiChargeItemSpace:
        return ProdigiChargeItemSpace(charge_item_data)

    @staticmethod
    def get_existing(session, prodigi_id: str) -> Union[ProdigiChargeItem, None]:
        return session.query(ProdigiChargeItem).filter(ProdigiChargeItem.prodigi_id == prodigi_id).first()

    def update(self, charge_item_data: Union[ProdigiChargeItemSpace, Dict[str, Any]],
               cost: ProdigiCost = None,
               charge: ProdigiCharge = None
               ):
        if not isinstance(charge_item_data, ProdigiChargeItemSpace):
            charge_item_data = self.create_namespace(charge_item_data)

        if self.description != charge_item_data.description:
            self.description = charge_item_data.description
        if self.item_sku != charge_item_data.item_sku:
            self.item_sku = charge_item_data.item_sku
        if self.shipment_id != charge_item_data.shipment_id:
            self.shipment_id = charge_item_data.shipment_id
        if self.item_id != charge_item_data.item_id:
            self.item_id = charge_item_data.item_id
        if self.merchant_item_reference != charge_item_data.merchant_item_reference:
            self.merchant_item_reference = charge_item_data.merchant_item_reference

        if cost is not None and self.cost != cost:
            self.cost = cost

        if charge is not None and self.charge != charge:
            self.charge = charge


class ProdigiStatus(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#status
    """
    __tablename__ = 'prodigi_status'
    id = Column(Integer, primary_key=True)
    stage = Column(Enum(Prodigi.StatusStage))
    download_assets = Column(Enum(Prodigi.DetailStatus))
    print_ready_assets_prepared = Column(Enum(Prodigi.DetailStatus))
    allocate_production_location = Column(Enum(Prodigi.DetailStatus))
    in_production = Column(Enum(Prodigi.DetailStatus))
    shipping = Column(Enum(Prodigi.DetailStatus))

    # relationships

    # one to one
    _order_id = Column(Integer, ForeignKey('prodigi_order.id'))
    order = relationship("ProdigiOrder", back_populates="status")

    # one to many
    issues = relationship("ProdigiIssue", back_populates="status", cascade="all, delete, delete-orphan")

    @classmethod
    def create(cls, status_data: Union[ProdigiStatusSpace, Dict[str, Any]],
               order: List[ProdigiOrder] = None,
               issues: List[ProdigiIssue] = None) -> ProdigiStatus:
        if not isinstance(status_data, ProdigiStatusSpace):
            status_data = cls.create_namespace(status_data)

        status = cls(
            stage=status_data.stage,
            download_assets=status_data.download_assets,
            print_ready_assets_prepared=status_data.print_ready_assets_prepared,
            allocate_production_location=status_data.allocate_production_location,
            in_production=status_data.in_production,
            shipping=status_data.shipping
        )

        if order is not None:
            status.order = order

        if issues is not None:
            status.issues = issues

        return status

    @staticmethod
    def create_namespace(status_data: Dict[str, Any]) -> ProdigiStatusSpace:
        return ProdigiStatusSpace(status_data)

    def update(self, status_data: Union[ProdigiStatusSpace, Dict[str, Any]],
               order: List[ProdigiOrder] = None,
               issues: List[ProdigiIssue] = None,
               overwrite_list: bool = False
               ):
        if not isinstance(status_data, ProdigiStatusSpace):
            status_data = self.create_namespace(status_data)

        if self.stage != status_data.stage:
            self.stage = status_data.stage
        if self.download_assets != status_data.download_assets:
            self.download_assets = status_data.download_assets
        if self.print_ready_assets_prepared != status_data.print_ready_assets_prepared:
            self.print_ready_assets_prepared = status_data.print_ready_assets_prepared
        if self.allocate_production_location != status_data.allocate_production_location:
            self.allocate_production_location = status_data.allocate_production_location
        if self.in_production != status_data.allocate_production_location:
            self.in_production = status_data.allocate_production_location
        if self.shipping != status_data.shipping:
            self.shipping = status_data.shipping

        if order is not None and self.order != order:
            self.order = order

        if issues is not None:
            self.issues = issues if overwrite_list else merge_lists(self.issues, issues)


class ProdigiIssue(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#status-status-object
    """
    __tablename__ = 'prodigi_issue'
    id = Column(Integer, primary_key=True)
    object_id = Column(String)
    error_code = Column(Enum(Prodigi.IssueErrorCode))
    description = Column(String)

    # relationships

    # many to one
    _status_id = Column(Integer, ForeignKey('prodigi_status.id'))
    status = relationship("ProdigiStatus", uselist=False, back_populates="issues")

    # one to one
    authorization_details = relationship("ProdigiAuthorizationDetails", uselist=False, back_populates='issue',
                                         cascade="all, delete, delete-orphan")

    @classmethod
    def create(cls, issue_data: Union[ProdigiIssueSpace, Dict[str, Any]],
               status: ProdigiStatus = None,
               authorization_details: ProdigiAuthorizationDetails = None
               ) -> ProdigiIssue:
        if not isinstance(issue_data, ProdigiIssueSpace):
            issue_data = cls.create_namespace(issue_data)

        issue = cls(
            object_id=issue_data.object_id,
            error_code=issue_data.error_code,
            description=issue_data.description
        )

        if status is not None:
            issue.status = status

        if authorization_details is not None:
            issue.authorization_details = authorization_details

        return issue

    @staticmethod
    def create_namespace(issue_data: Dict[str, Any]) -> ProdigiIssueSpace:
        return ProdigiIssueSpace(issue_data)

    def alert_string(self):
        alert_string = ''
        alert_string += f'Object ID: {self.object_id}\n' if self.object_id else ''
        alert_string += f'Error code: {self.error_code}\n' if self.error_code else ''
        alert_string += f'Description: {self.description}\n' if self.description else ''

        return alert_string

    def update(self, issue_data: Union[ProdigiIssueSpace, Dict[str, Any]],
               status: ProdigiStatus = None,
               authorization_details: ProdigiAuthorizationDetails = None
               ):
        if not isinstance(issue_data, ProdigiIssueSpace):
            issue_data = self.create_namespace(issue_data)

        if self.object_id != issue_data.object_id:
            self.object_id = issue_data.object_id
        if self.error_code != issue_data.error_code:
            self.error_code = issue_data.error_code
        if self.description != issue_data.description:
            self.description = issue_data.description

        if status is not None and self.status != status:
            self.status = status

        if authorization_details is not None and self.authorization_details != authorization_details:
            self.authorization_details = authorization_details


class ProdigiAuthorizationDetails(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#status-status-authorisation-details
    """
    __tablename__ = 'prodigi_authorization_details'
    id = Column(Integer, primary_key=True)
    authorization_url = Column(String)

    # relationships

    # one to one
    _issue_id = Column(Integer, ForeignKey('prodigi_issue.id'))
    issue = relationship("ProdigiIssue", uselist=False, back_populates="authorization_details")

    payment_details = relationship("ProdigiCost", uselist=False, back_populates="authorization",
                                   cascade="all, delete, delete-orphan")

    @classmethod
    def create(cls, authorization_detail_data: Union[ProdigiAuthorizationDetailsSpace, Dict[str, Any]],
               issues: List[ProdigiIssue] = None,
               payment_details: ProdigiCost = None
               ) -> ProdigiAuthorizationDetails:
        if not isinstance(authorization_detail_data, ProdigiAuthorizationDetails):
            authorization_detail_data = cls.create_namespace(authorization_detail_data)

        authorization_detail = cls(
            authorization_url=authorization_detail_data.authorization_url
        )

        if issues is not None:
            authorization_detail.issues = issues

        if payment_details is not None:
            authorization_detail.payment_details = payment_details

        return authorization_detail

    @staticmethod
    def create_namespace(authorization_detail_data: Dict[str, Any]) -> ProdigiAuthorizationDetails:
        return ProdigiAuthorizationDetails(authorization_detail_data)

    def update(self, authorization_detail_data: Union[ProdigiAuthorizationDetailsSpace, Dict[str, Any]],
               issue: ProdigiIssue = None,
               payment_details: ProdigiCost = None,
               overwrite_list: bool = False
               ):
        if not isinstance(authorization_detail_data, ProdigiAuthorizationDetails):
            authorization_detail_data = self.create_namespace(authorization_detail_data)

        if self.authorization_url != authorization_detail_data.authorization_url:
            self.authorization_url = authorization_detail_data.authorization_url

        if issue is not None and self.issue != issue:
            self.issue = issue

        if payment_details is not None and self.payment_details != payment_details:
            self.payment_details = payment_details


class ProdigiCost(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object
    """
    __tablename__ = 'prodigi_cost'
    id = Column(Integer, primary_key=True)
    amount = Column(String)
    currency = Column(String)

    # relationships

    # one to one
    _authorization_id = Column(Integer, ForeignKey('prodigi_authorization_details.id'))
    authorization = relationship("ProdigiAuthorizationDetails", back_populates="payment_details")
    _charge_id = Column(Integer, ForeignKey('prodigi_charge.id'))
    charge = relationship("ProdigiCharge", back_populates="total_cost")
    _charge_item_id = Column(Integer, ForeignKey('prodigi_charge_item.id'))
    charge_item = relationship("ProdigiChargeItem", back_populates="cost")
    _item_id = Column(Integer, ForeignKey('prodigi_item.id'))
    item = relationship("ProdigiItem", back_populates="recipient_cost")

    @classmethod
    def create(cls, cost_data: Union[ProdigiCostSpace, Dict[str, Any]],
               authorization: ProdigiAuthorizationDetails = None,
               charge: ProdigiCharge = None,
               charge_item: ProdigiChargeItem = None,
               item: ProdigiItem = None
               ) -> ProdigiCost:
        if not isinstance(cost_data, ProdigiCostSpace):
            cost_data = cls.create_namespace(cost_data)

        cost = cls(
            amount=cost_data.amount,
            currency=cost_data.currency
        )

        if authorization is not None:
            cost.authorization = authorization

        if charge is not None:
            cost.charge = charge

        if charge_item is not None:
            cost.charge_item = charge_item

        if item is not None:
            cost.item = item

        return cost

    @staticmethod
    def create_namespace(cost_data: Dict[str, Any]) -> ProdigiCostSpace:
        return ProdigiCostSpace(cost_data)

    def update(self, cost_data: Union[ProdigiCostSpace, Dict[str, Any]],
               authorization: ProdigiAuthorizationDetails = None,
               charge: ProdigiCharge = None,
               charge_item: ProdigiChargeItem = None,
               item: ProdigiItem = None
               ):
        if not isinstance(cost_data, ProdigiCostSpace):
            cost_data = self.create_namespace(cost_data)

        if self.amount != cost_data.amount:
            self.amount = cost_data.amount
        if self.currency != cost_data.currency:
            self.currency = cost_data.currency

        if authorization is not None and self.authorization != authorization:
            self.authorization = authorization

        if charge is not None and self.charge != charge:
            self.charge = charge

        if charge_item is not None and self.charge_item != charge_item:
            self.charge_item = charge_item

        if item is not None and self.item != item:
            self.item = item


def create_database():
    engine = make_engine()
    Base.metadata.create_all(engine)
