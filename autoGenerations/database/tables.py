from __future__ import annotations
from typing import List, Union, Dict, Any
from database.utils import Base, make_engine
from database.enums import Etsy
from database.namespaces import EtsyReceiptSpace, EtsyReceiptShipmentSpace, EtsySellerSpace, EtsyBuyerSpace, \
    EtsyTransactionSpace, AddressSpace, EtsyProductPropertySpace, EtsyProductSpace, EtsyShippingProfileSpace, \
    EtsyProductionPartnerSpace, EtsyListingSpace, EtsyOfferingSpace, EtsyShopSectionSpace, EtsyReturnPolicySpace, \
    EtsyShippingProfileUpgradeSpace, EtsyShippingProfileDestinationSpace, EtsyShopSpace

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, ForeignKey, Enum, Table

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


# Thread on SQL UPDATE when you are 'changing' a table column value with the value it already is:
# https://www.sqlservercentral.com/forums/topic/update-when-the-values-are-the-same. Apparently SQL
# still marks the disk record as dirty and sends an update. So have to do check in all of the update methods to make
# most efficient transaction

# TODO: Review the get_existing methods


class EtsyReceipt(Base):
    """
    API Reference: https://developer.etsy.com/documentation/reference#operation/getShopReceipt
    """
    __tablename__ = 'etsy_receipt'
    id = Column(Integer, primary_key=True)
    receipt_id = Column(BigInteger, unique=True)
    receipt_type = Column(Integer)
    status = Column(Enum(Etsy.OrderStatus))
    payment_method = Column(String)
    message_from_seller = Column(String)
    message_from_buyer = Column(String)
    message_from_payment = Column(String)
    is_paid = Column(Boolean)
    is_shipped = Column(Boolean)
    create_timestamp = Column(BigInteger)
    created_timestamp = Column(BigInteger)
    update_timestamp = Column(BigInteger)
    updated_timestamp = Column(BigInteger)
    is_gift = Column(Boolean)
    gift_message = Column(String)
    grand_total = Column(Float)
    sub_total = Column(Float)
    total_price = Column(Float)
    shipping_cost = Column(Float)
    tax_cost = Column(Float)
    vat_cost = Column(Float)
    discount = Column(Float)
    gift_wrap_price = Column(Float)

    # relationships
    _address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship("Address", uselist=False, back_populates='receipts')
    _buyer_id = Column(Integer, ForeignKey('etsy_buyer.id'))
    buyer = relationship("EtsyBuyer", uselist=False, back_populates='receipts')
    _seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates='receipts')

    transactions = relationship("EtsyTransaction", back_populates='receipt')
    receipt_shipments = relationship("EtsyReceiptShipment", back_populates='receipt')

    @classmethod
    def create(cls, receipt_data: Union[EtsyReceiptSpace, Dict[str, Any]],
               address: Address = None,
               buyer: EtsyBuyer = None,
               seller: EtsySeller = None,
               transactions: List[EtsyTransaction] = None,
               receipt_shipments: List[EtsyReceiptShipment] = None
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
            sub_total=receipt_data.sub_total,
            total_price=receipt_data.total_price,
            shipping_cost=receipt_data.shipping_cost,
            tax_cost=receipt_data.tax_cost,
            vat_cost=receipt_data.vat_cost,
            discount=receipt_data.discount,
            gift_wrap_price=receipt_data.gift_wrap_price
        )

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

        return receipt

    @staticmethod
    def create_namespace(etsy_receipt: Dict[str, Any]) -> EtsyReceiptSpace:
        return EtsyReceiptSpace(etsy_receipt)

    @staticmethod
    def get_existing(session, receipt_id: int) -> Union[None, EtsyReceipt]:
        return session.query(EtsyReceipt).filter(EtsyReceipt.receipt_id == receipt_id).first()


class EtsySeller(Base):
    __tablename__ = 'etsy_seller'
    id = Column(Integer, primary_key=True)
    seller_id = Column(BigInteger, unique=True)
    email = Column(String)

    # relationships
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
            EtsySeller.seller_id == seller_id
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
        self.email = seller_data.email

        if receipts is not None:
            self.receipts = receipts if overwrite_list else self.receipts + receipts

        if transactions:
            self.transactions = transactions if overwrite_list else self.transactions + transactions

        if listings is not None:
            self.listings = listings if overwrite_list else self.listings + listings

        if shipping_profiles is not None:
            self.shipping_profiles = shipping_profiles if overwrite_list else self.shipping_profiles + shipping_profiles

        if shop_sections is not None:
            self.shop_sections = shop_sections if overwrite_list else self.shop_sections + shop_sections

        if shops is not None:
            self.shops = shops if overwrite_list else self.shops + shops


class EtsyBuyer(Base):
    __tablename__ = 'etsy_buyer'
    id = Column(Integer, primary_key=True)
    buyer_id = Column(BigInteger, unique=True)
    email = Column(String)

    receipts = relationship('EtsyReceipt', back_populates='buyer')
    transactions = relationship("EtsyTransaction", back_populates='buyer')

    @classmethod
    def create(cls, buyer_data: Union[EtsyBuyerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None,
               transactions: List[EtsyTransaction] = None
               ) -> EtsyBuyer:
        if not isinstance(buyer_data, EtsyBuyerSpace):
            buyer_data = cls.create_namespace(buyer_data)

        buyer = cls(
            buyer_id=buyer_data.buyer_id,
            email=buyer_data.email
        )

        if receipts is not None:
            buyer.receipts = receipts

        if transactions is not None:
            buyer.transactions = transactions

        return buyer

    @staticmethod
    def create_namespace(buyer_data: Dict[str, Any]):
        return EtsyBuyerSpace(buyer_data)

    @staticmethod
    def get_existing(session, buyer_id: int) -> Union[None, EtsyBuyer]:
        return session.query(EtsyBuyer).filter(
            EtsyBuyer.buyer_id == buyer_id
        ).first()

    def update(self, buyer_data: Union[EtsyBuyerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None,
               transactions: List[EtsyTransaction] = None,
               overwrite_list: bool = False):
        if not isinstance(buyer_data, EtsyBuyerSpace):
            buyer_data = self.create_namespace(buyer_data)
        self.email = buyer_data.email

        if receipts is not None:
            self.receipts = receipts if overwrite_list else self.receipts + receipts

        if transactions:
            self.transactions = transactions if overwrite_list else self.transactions + transactions


class Address(Base):
    __tablename__ = 'address'
    id = Column(Integer, primary_key=True)
    first_line = Column(String)
    second_line = Column(String)
    city = Column(String)
    state = Column(String)
    zip_code = Column(String)
    country = Column(String)
    formatted = Column(String)

    receipts = relationship('EtsyReceipt', back_populates='address')

    @classmethod
    def create(cls, address_data: Union[AddressSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None) -> Address:
        if not isinstance(address_data, AddressSpace):
            address_data = cls.create_namespace(address_data)

        address = Address(
            first_line=address_data.first_line,
            second_line=address_data.second_line,
            city=address_data.city,
            state=address_data.state,
            zip_code=address_data.zip,
            country=address_data.country,
            formatted=address_data.formatted_address
        )

        if receipts is not None:
            address.receipts = receipts

        return address

    @staticmethod
    def create_namespace(address_data: Dict[str, Any]):
        return AddressSpace(address_data)

    @staticmethod
    def get_existing(session, zip_code: str, city: str, state: str, country: str, first_line: str,
                     second_line: str) -> Union[None, Address]:
        return session.query(Address).filter(
            Address.zip == zip_code,
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
    create_timestamp = Column(BigInteger)
    paid_timestamp = Column(BigInteger)
    shipped_timestamp = Column(BigInteger)
    quantity = Column(Integer)
    is_digital = Column(Boolean)
    file_data = Column(String)
    transaction_type = Column(String)
    price = Column(Float)
    shipping_cost = Column(Float)
    min_processing_days = Column(Integer)
    max_processing_days = Column(Integer)
    shipping_method = Column(String)
    shipping_upgrade = Column(String)
    expected_ship_date = Column(BigInteger)
    buyer_coupon = Column(Integer)
    shop_coupon = Column(Integer)

    # relationships
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

    # Many to Many relationship
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
            file_data=transaction_data.file_date,
            transaction_type=transaction_data.transaction_type,
            price=transaction_data.price,
            shipping_cost=transaction_data.shipping_cost,
            min_processing_days=transaction_data.min_processing_days,
            max_processing_days=transaction_data.max_processing_days,
            shipping_method=transaction_data.shipping_method,
            shipping_upgrade=transaction_data.shipping_upgrade,
            expected_ship_date=transaction_data.expected_ship_date,
            buyer_coupon=transaction_data.buyer_coupon,
            shop_coupon=transaction_data.shop_coupon,
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
            EtsyTransaction.transaction_id == transaction_id
        ).first()

    def update(self, transaction_data: Union[EtsyTransactionSpace, Dict[str, Any]],
               buyer: EtsyBuyer = None,
               seller: EtsySeller = None,
               shipping_profile: EtsyShippingProfile = None,
               product: EtsyProduct = None,
               receipt: EtsyReceipt = None,
               product_properties: List[EtsyProductProperty] = None,
               overwrite_list: bool = False):
        if not isinstance(transaction_data, EtsyTransactionSpace):
            transaction_data = self.create_namespace(transaction_data)

        self.transaction_id = transaction_data.transaction_id
        self.title = transaction_data.title
        self.description = transaction_data.description
        self.create_timestamp = transaction_data.create_timestamp
        self.paid_timestamp = transaction_data.paid_timestamp
        self.shipped_timestamp = transaction_data.shipped_timestamp
        self.quantity = transaction_data.quantity
        self.is_digital = transaction_data.is_digital
        self.file_data = transaction_data.file_date
        self.transaction_type = transaction_data.transaction_type
        self.price = transaction_data.price
        self.shipping_cost = transaction_data.shipping_cost
        self.min_processing_days = transaction_data.min_processing_days
        self.max_processing_days = transaction_data.max_processing_days
        self.shipping_method = transaction_data.shipping_method
        self.shipping_upgrade = transaction_data.shipping_upgrade
        self.expected_ship_date = transaction_data.expected_ship_date
        self.buyer_coupon = transaction_data.buyer_coupon
        self.shop_coupon = transaction_data.shop_coupon

        if buyer is not None:
            self.buyer = buyer

        if seller is not None:
            self.seller = seller

        if shipping_profile is not None:
            self.shipping_profile = shipping_profile

        if product is not None:
            self.product = product

        if receipt is not None:
            self.receipt = receipt

        if product_properties is not None:
            self.product_properties = product_properties if overwrite_list else self.product_properties \
                                                                                + product_properties


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
    transactions = relationship("EtsyTransaction", back_populates='product')
    offerings = relationship("EtsyOffering", back_populates='product')
    properties = relationship("EtsyProductProperty", back_populates='products')
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
            price=product_data.price
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
        return session.query(EtsyProduct).filter(EtsyProduct.product_id == product_id).first()

    def update(self, product_data: Union[EtsyProductSpace, Dict[str, Any]],
               transactions: List[EtsyTransaction] = None,
               offerings: List[EtsyOffering] = None,
               properties: List[EtsyProductProperty] = None,
               listings: List[EtsyListing] = None,
               overwrite_lists: Boolean = False
               ):
        if not isinstance(product_data, EtsyProductSpace):
            product_data = self.create_namespace(product_data)

        self.product_id = (self.product_id, product_data.product_id)
        self.sku = (self.sku, product_data.sku)
        self.price = (self.price, product_data.price)

        if transactions is not None:
            self.transactions = transactions if overwrite_lists else self.transactions + transactions

        if offerings is not None:
            self.offerings = offerings if overwrite_lists else self.offerings + offerings

        if properties is not None:
            self.properties = properties if overwrite_lists else self.properties + properties

        if listings is not None:
            self.listings = listings if overwrite_lists else self.listings + listings


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
    _seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates="shipping_profiles")
    destinations = relationship("EtsyShippingProfileDestination", back_populates='shipping_profile')
    upgrades = relationship("EtsyShippingProfileUpgrade", back_populates='shipping_profile')
    transactions = relationship("EtsyTransaction", back_populates='shipping_profile')
    listings = relationship("EtsyListing", back_populates="shipping_profile")

    @classmethod
    def create(cls, shipping_profile_data: Union[EtsyShippingProfile, Dict[str, Any]],
               seller: EtsySeller = None,
               destinations: List[EtsyShippingProfileDestination] = None,
               upgrades: List[EtsyShippingProfileUpgrade] = None,
               transactions: List[EtsyTransaction] = None,
               listings: List[EtsyListing] = None
               ) -> EtsyShippingProfile:
        if not isinstance(shipping_profile_data, EtsyProductSpace):
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
            EtsyShippingProfile.shipping_profile_id == shipping_profile_id
        ).first()

    def update(self, shipping_profile_data: Union[EtsyShippingProfile, Dict[str, Any]],
               seller: EtsySeller = None,
               destinations: List[EtsyShippingProfileDestination] = None,
               upgrades: List[EtsyShippingProfileUpgrade] = None,
               transactions: List[EtsyTransaction] = None,
               listings: List[EtsyListing] = None,
               overwrite_lists: Boolean = False
               ):
        if not isinstance(shipping_profile_data, EtsyShippingProfileSpace):
            shipping_profile_data = self.create_namespace(shipping_profile_data)

        self.shipping_profile_id = (self.shipping_profile_id, shipping_profile_data.shipping_profile_id)
        self.title = (self.title, shipping_profile_data.title)
        self.min_processing_days = (self.min_processing_days, shipping_profile_data.min_processing_days)
        self.max_processing_days = (self.max_processing_days, shipping_profile_data.max_processing_days)
        self.processing_days_display_label = (self.processing_days_display_label,
                                              shipping_profile_data.processing_days_display_label)
        self.origin_country_iso = (self.origin_country_iso, shipping_profile_data.origin_country_iso)
        self.is_deleted = (self.is_deleted, shipping_profile_data.is_deleted)
        self.origin_postal_code = (self.origin_postal_code, shipping_profile_data.origin_postal_code)
        self.profile_type = (self.profile_type, shipping_profile_data.profile_type)
        self.domestic_handling_fee = (self.domestic_handling_fee, shipping_profile_data.domestic_handling_fee)
        self.internation_handling_fee = (self.internation_handling_fee,
                                         shipping_profile_data.international_handling_fee)

        if seller is not None:
            self.seller = seller

        if destinations is not None:
            self.destinations = destinations if overwrite_lists else self.destinations + destinations

        if upgrades is not None:
            self.upgrades = upgrades if overwrite_lists else self.upgrades + upgrades

        if transactions is not None:
            self.transactions = transactions if overwrite_lists else self.transactions + transactions

        if listings is not None:
            self.listings = listings if overwrite_lists else self.listings + listings


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
    primary_cost = Column(Float)
    secondary_cost = Column(Float)

    # TODO: There is no endpoint to get a single shipping carrier's information. If this turns out to be important,
    #  we can retrieve all shipping carriers periodically and then keep a record of them in the database so that we can
    #  create a relationship here
    shipping_carrier_id = Column(Integer)
    mail_class = Column(String)
    min_delivery_days = Column(Integer)
    max_delivery_days = Column(Integer)

    # relationships
    _shipping_profile_id = Column(Integer, ForeignKey('etsy_shipping_profile.id'))
    shipping_profile = relationship("EtsyShippingProfile", uselist=False, back_populates="destinations")

    @classmethod
    def create(cls, shipping_destination_data: Union[EtsyShippingProfileDestination, Dict[str, Any]],
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
            secondary_cost=shipping_destination_data.secondary_cost,
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
            EtsyShippingProfileDestination.shipping_profile_destination_id == shipping_destination_id
        ).first()

    def update(self, shipping_destination_data: Union[EtsyShippingProfileDestination, Dict[str, Any]],
               shipping_profile: EtsyShippingProfile = None
               ):
        if not isinstance(shipping_destination_data, EtsyShippingProfileDestinationSpace):
            shipping_destination_data = self.create_namespace(shipping_destination_data)

        self.shipping_profile_destination_id = (self.shipping_profile_destination_id,
                                                shipping_destination_data.shipping_profile_destination_id)
        self.origin_country_iso = (self.origin_country_iso, shipping_destination_data.origin_country_iso)
        self.destination_country_iso = (self.destination_country_iso,
                                        shipping_destination_data.destination_country_iso)
        self.destination_region = (self.destination_region, shipping_destination_data.destination_region)
        self.primary_cost = (self.primary_cost, shipping_destination_data.primary_cost)
        self.secondary_cost = (self.secondary_cost, shipping_destination_data.secondary_cost)
        self.shipping_carrier_id = (self.shipping_carrier_id, shipping_destination_data.shipping_carrier_id)
        self.mail_class = (self.mail_class, shipping_destination_data.mail_class)
        self.min_delivery_days = (self.min_delivery_days, shipping_destination_data.min_delivery_days)
        self.max_delivery_days = (self.max_delivery_days, shipping_destination_data.max_delivery_days)

        if shipping_profile is not None:
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
    price = Column(Float)
    secondary_price = Column(Float)

    # TODO: There is no endpoint to get a single shipping carrier's information. If this turns out to be important,
    #  we can retrieve all shipping carriers periodically and then keep a record of them in the database so that we can
    #  create a relationship here
    shipping_carrier_id = Column(String)
    mail_class = Column(String)
    min_delivery_days = Column(Integer)
    max_delivery_days = Column(Integer)

    # relationships
    _shipping_profile_id = Column(Integer, ForeignKey('etsy_shipping_profile.id'))
    shipping_profile = relationship("EtsyShippingProfile", uselist=False, back_populates="upgrades")

    @classmethod
    def create(cls, shipping_upgrade_data: Union[EtsyShippingProfileUpgrade, Dict[str, Any]],
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
            secondary_price=shipping_upgrade_data.secondary_price,
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
            EtsyShippingProfileUpgrade.upgrade_id == shipping_upgrade_id
        ).first()

    def update(self, shipping_upgrade_data: Union[EtsyShippingProfileUpgrade, Dict[str, Any]],
               shipping_profile: EtsyShippingProfile = None
               ):
        if not isinstance(shipping_upgrade_data, EtsyShippingProfileUpgradeSpace):
            shipping_upgrade_data = self.create_namespace(shipping_upgrade_data)

        self.upgrade_id = (self.upgrade_id, shipping_upgrade_data.upgrade_id)
        self.upgrade_name = (self.upgrade_name, shipping_upgrade_data.upgrade_name)
        self.type = (self.type, shipping_upgrade_data.type)
        self.rank = (self.rank, shipping_upgrade_data.rank)
        self.language = (self.language, shipping_upgrade_data.language)
        self.price = (self.price, shipping_upgrade_data.price)
        self.secondary_price = (self.secondary_price, shipping_upgrade_data.secondary_price)
        self.shipping_carrier_id = (self.shipping_carrier_id, shipping_upgrade_data.shipping_carrier_id)
        self.mail_class = (self.mail_class, shipping_upgrade_data.mail_class)
        self.min_delivery_days = (self.min_delivery_days, shipping_upgrade_data.min_delivery_days)
        self.max_delivery_days = (self.max_delivery_days, shipping_upgrade_data.max_delivery_days)

        if shipping_profile is not None:
            self.shipping_profile = shipping_profile


class EtsyReceiptShipment(Base):
    """
    https://developer.etsy.com/documentation/reference/#operation/getShopReceipt
    """
    __tablename__ = 'etsy_shipment'
    id = Column(Integer, primary_key=True)
    receipt_shipping_id = Column(BigInteger, unique=True)
    shipment_notification_timestamp = Column(BigInteger)
    carrier_name = Column(String)
    tracking_code = Column(String)

    # relationships
    _receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
    receipt = relationship('EtsyReceipt', uselist=False, back_populates='receipt_shipments')

    @classmethod
    def create(cls, receipt_shipment_data: Union[EtsyReceiptShipmentSpace, Dict[str, Any]],
               receipt: EtsyReceipt = None) -> EtsyReceiptShipment:
        if not isinstance(receipt_shipment_data, EtsyProductSpace):
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
            EtsyReceiptShipment.receipt_shipping_id == receipt_shipping_id
        )

    def update(self, receipt_shipment_data: Union[EtsyReceiptShipmentSpace, Dict[str, Any]],
               receipt: EtsyReceipt = None):
        if not isinstance(receipt_shipment_data, EtsyProductSpace):
            receipt_shipment_data = self.create_namespace(receipt_shipment_data)

        self.shipment_notification_timestamp = receipt_shipment_data.shipment_notification_timestamp
        self.carrier_name = receipt_shipment_data.carrier_name
        self.tracking_code = receipt_shipment_data.tracking_code

        if receipt is not None:
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
    _product_id = Column(Integer, ForeignKey('etsy_product.id'))
    product = relationship("EtsyProduct", uselist=False, back_populates='properties')
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
            EtsyProductProperty.property_id == property_id
        ).filter(
            EtsyProductProperty.property_name == property_name
        ).first()

    def update(self, property_data: Union[EtsyProductPropertySpace, Dict[str, Any]],
               transactions: List[EtsyTransaction] = None,
               overwrite_lists: bool = False):
        if not isinstance(property_data, EtsyProductPropertySpace):
            property_data = self.create_namespace(property_data)

        self.property_id = property_data.property_id
        self.property_name = property_data.property_name
        self.scale_id = property_data.scale_id
        self.scale_name = property_data.scale_name

        if transactions is not None:
            self.transactions = transactions if overwrite_lists else self.transactions + transactions


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
    creation_timestamp = Column(BigInteger)
    created_timestamp = Column(BigInteger)
    ending_timestamp = Column(BigInteger)
    original_creation_timestamp = Column(BigInteger)
    last_modified_timestamp = Column(BigInteger)
    updated_timestamp = Column(BigInteger)
    state_timestamp = Column(BigInteger)
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
    price = Column(Float)
    taxonomy_id = Column(Integer)
    skus = Column(String)
    views = Column(Integer)

    # relationships
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
            EtsyListing.listing_id == listing_id
        ).first()

    def update(self, listing_data: Union[EtsyListingSpace, Dict[str, Any]],
               shipping_profile: EtsyShippingProfile = None,
               seller: EtsySeller = None,
               shop: EtsyShop = None,
               shop_section: EtsyShopSection = None,
               return_policy: EtsyReturnPolicy = None,
               products: List[EtsyProduct] = None,
               production_partners: List[EtsyProductionPartner] = None,
               overwrite_list: Boolean = False
               ):
        if not isinstance(listing_data, EtsyListingSpace):
            listing_data = self.create_namespace(listing_data)

        if self.listing_id != listing_data.listing_id:
            self.listing_id = (self.listing_id, listing_data.listing_id)
        self.title = listing_data.title
        self.description = listing_data.description
        self.state = listing_data.state
        self.creation_timestamp = listing_data.creation_timestamp
        self.created_timestamp = listing_data.created_timestamp
        self.ending_timestamp = listing_data.ending_timestamp
        self.original_creation_timestamp = listing_data.original_creation_timestamp
        self.last_modified_timestamp = listing_data.last_modified_timestamp
        self.updated_timestamp = listing_data.updated_timestamp
        self.state_timestamp = listing_data.state_timestamp
        self.quantity = listing_data.quantity
        self.featured_rank = listing_data.featured_rank
        self.url = listing_data.url
        self.num_favorers = listing_data.num_favorers
        self.non_taxable = listing_data.non_taxable
        self.is_taxable = listing_data.is_taxable
        self.is_customizable = listing_data.is_customizable
        self.is_personalizable = listing_data.is_personalizable
        self.personalization_is_required = listing_data.personalization_is_required
        self.personalization_char_count_max = listing_data.personalization_char_count_max
        self.personalization_instructions = listing_data.personalization_instructions
        self.listing_type = listing_data.listing_type
        self.tags = listing_data.tags
        self.materials = listing_data.materials
        self.processing_min = listing_data.processing_min
        self.processing_max = listing_data.processing_max
        self.who_made = listing_data.who_made
        self.when_made = listing_data.when_made
        self.is_supply = listing_data.is_supply
        self.item_weight = listing_data.item_weight
        self.item_weight_unit = listing_data.item_weight_unit
        self.item_length = listing_data.item_length
        self.item_width = listing_data.item_width
        self.item_height = listing_data.item_height
        self.item_dimensions_unit = listing_data.item_dimensions_unit
        self.is_private = listing_data.is_private
        self.style = listing_data.style
        self.file_data = listing_data.file_data
        self.has_variations = listing_data.has_variations
        self.should_auto_renew = listing_data.should_auto_renew
        self.language = listing_data.language
        self.price = listing_data.price
        self.taxonomy_id = listing_data.taxonomy_id
        self.skus = listing_data.skus
        self.views = listing_data.views

        if shipping_profile is not None:
            self.shipping_profile = shipping_profile

        if seller is not None:
            self.seller = seller

        if shop is not None:
            self.shop = shop

        if shop_section is not None:
            self.shop_section = shop_section

        if return_policy is not None:
            self.return_policy = return_policy

        if production_partners is not None:
            self.production_partners = production_partners if overwrite_list else \
                self.production_partners + production_partners

        if products is not None:
            self.products = products if overwrite_list else self.products + production_partners


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
    _shop_id = Column(Integer, ForeignKey("etsy_shop.id"))
    shop = relationship("EtsyShop", uselist=False, back_populates="return_policies")
    listings = relationship("EtsyListing", back_populates="return_policy")

    @classmethod
    def create(cls, return_policy_data: Union[EtsyReturnPolicy, Dict[str, Any]],
               shop: EtsyShop = None,
               listings: List[EtsyListing] = None) -> EtsyReturnPolicy:
        if not isinstance(return_policy_data, EtsyReturnPolicySpace):
            return_policy_data = cls.create_namespace(return_policy_data)

        return_policy = cls(
            return_policy_id=return_policy_data.return_policy_id,
            accepts_returns=return_policy_data.accepts_return,
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
            EtsyReturnPolicy.return_policy_id == return_policy_id
        ).first()

    def update(self, return_policy_data: Union[EtsyReturnPolicy, Dict[str, Any]],
               shop: EtsyShop = None,
               listings: List[EtsyListing] = None,
               overwrite_list: Boolean = False):
        if not isinstance(return_policy_data, EtsyReturnPolicySpace):
            return_policy_data = self.create_namespace(return_policy_data)

        self.return_policy_id = return_policy_data.return_policy_id
        self.accepts_returns = return_policy_data.accepts_return
        self.accepts_exchanges = return_policy_data.accepts_exchanges
        self.return_deadline = return_policy_data.return_deadline

        if shop is not None:
            self.shop = shop

        if listings is not None:
            self.listings = listings if overwrite_list else self.listings + listings


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
    _seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates="shop_sections")
    _shop_id = Column(Integer, ForeignKey('etsy_shop.id'))
    shop = relationship("EtsyShop", uselist=False, back_populates="shop_sections")
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
            EtsyShopSection.shop_section_id == shop_section_id
        ).first()

    def update(self, shop_section_data: Union[EtsyShopSectionSpace, Dict[str, Any]],
               seller: EtsySeller = None, shop: EtsyShop = None,
               listings: List[EtsyListing] = None,
               overwrite_list: Boolean = False):
        if not isinstance(shop_section_data, EtsyShopSectionSpace):
            shop_section_data = self.create_namespace(shop_section_data)

        self.shop_section_id = shop_section_data.shop_section_id
        self.title = shop_section_data.title
        self.rank = shop_section_data.rank
        self.active_listing_count = shop_section_data.active_listing_count

        if seller is not None:
            self.seller = seller

        if shop is not None:
            self.shop = shop

        if listings is not None:
            self.listings = listings if overwrite_list else self.listings + listings


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
            EtsyProductionPartner.production_partner_id == production_partner_id
        ).first()

    def update(self, production_partner_data: Union[EtsyProductionPartnerSpace, Dict[str, Any]],
               listings: List[EtsyListing] = None,
               overwrite_list: Boolean = False):
        if not isinstance(production_partner_data, EtsyProductionPartnerSpace):
            production_partner_data = self.create_namespace(production_partner_data)

        self.production_partner_id = production_partner_data.production_partner_id,
        self.partner_name = production_partner_data.partner_name,
        self.location = production_partner_data.location

        if listings is not None:
            self.listings = listings if overwrite_list else self.listings + listings


class EtsyShop(Base):
    """
    https://developer.etsy.com/documentation/reference#operation/getShop
    """
    __tablename__ = 'etsy_shop'
    id = Column(Integer, primary_key=True)
    shop_id = Column(BigInteger, unique=True)
    shop_name = Column(String)
    create_date = Column(Integer)
    created_date = Column(Integer)
    title = Column(String)
    announcement = Column(String)
    currency_code = Column(String)
    is_vacation = Column(Boolean)
    vacation_message = Column(String)
    sale_message = Column(String)
    digital_sale_message = Column(String)
    update_date = Column(Integer)
    updated_timestamp = Column(Integer)
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
    policy_update_date = Column(Integer)
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
    _seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates="shops")
    listings = relationship("EtsyListing", back_populates="shop")
    return_policies = relationship("EtsyReturnPolicy", back_populates="shop")
    shop_sections = relationship("EtsyShopSection", back_populates="shop")

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
            created_date=shop_data.created_date,
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
            transaction_sold_count=shop_data.transaction_sold_account,
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
            EtsyShop.shop_id == shop_id
        ).first()

    def update(self, shop_data: Union[EtsyShopSpace, Dict[str, Any]],
               seller: EtsySeller = None,
               listings: List[EtsyListing] = None,
               return_policies: List[EtsyReturnPolicy] = None,
               shop_sections: List[EtsyShopSection] = None,
               overwrite_list: Boolean = False
               ):
        if not isinstance(shop_data, EtsyShopSpace):
            shop_data = self.create_namespace(shop_data)

        self.shop_id = shop_data.shop_id,
        self.shop_name = shop_data.shop_name,
        self.create_date = shop_data.create_date,
        self.created_date = shop_data.created_date,
        self.title = shop_data.title,
        self.announcement = shop_data.announcement,
        self.currency_code = shop_data.currency_code,
        self.is_vacation = shop_data.is_vacation,
        self.vacation_message = shop_data.vacation_message,
        self.sale_message = shop_data.sale_message,
        self.digital_sale_message = shop_data.digital_sale_message,
        self.update_date = shop_data.update_date,
        self.updated_timestamp = shop_data.updated_timestamp,
        self.listing_active_count = shop_data.listing_active_count,
        self.digital_listing_count = shop_data.digital_listing_count,
        self.login_name = shop_data.login_name,
        self.accepts_custom_requests = shop_data.accepts_custom_requests,
        self.policy_welcome = shop_data.policy_welcome,
        self.policy_payment = shop_data.policy_payment,
        self.policy_shipping = shop_data.policy_shipping,
        self.policy_refunds = shop_data.policy_refunds,
        self.policy_additional = shop_data.policy_additional,
        self.policy_seller_info = shop_data.policy_seller_info,
        self.policy_update_date = shop_data.policy_update_date,
        self.policy_has_private_receipt_info = shop_data.policy_has_private_receipt_info,
        self.has_unstructured_policies = shop_data.has_unstructured_policies,
        self.policy_privacy = shop_data.policy_privacy,
        self.vacation_autoreply = shop_data.vacation_autoreply,
        self.url = shop_data.url,
        self.image_url_760x100 = shop_data.image_url_760x100,
        self.num_favorers = shop_data.num_favorers,
        self.languages = shop_data.languages,
        self.icon_url_fullxfull = shop_data.icon_url_fullxfull,
        self.is_using_structured_policies = shop_data.is_using_structured_policies,
        self.has_onboarded_structured_policies = shop_data.has_onboarded_structured_policies,
        self.include_dispute_form_link = shop_data.include_dispute_form_link,
        self.is_etsy_payments_onboarded = shop_data.is_etsy_payments_onboarded,
        self.is_calculated_eligible = shop_data.is_calculated_eligible,
        self.is_opted_into_buyer_promise = shop_data.is_opted_into_buyer_promise,
        self.is_shop_us_based = shop_data.is_shop_us_based,
        self.transaction_sold_count = shop_data.transaction_sold_account,
        self.shipping_from_country_iso = shop_data.shipping_from_country_iso,
        self.shop_location_country_iso = shop_data.shop_location_country_iso,
        self.review_count = shop_data.review_count,
        self.review_average = shop_data.review_average

        if seller is not None:
            self.seller = seller

        if listings is not None:
            self.listings = listings if overwrite_list else self.listings + listings

        if return_policies is not None:
            self.return_policies = return_policies if overwrite_list else self.return_policies + return_policies

        if shop_sections is not None:
            self.shop_sections = shop_sections if overwrite_list else self.shop_sections + shop_sections


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
    price = Column(Float)

    # relationships
    product_id = Column(Integer, ForeignKey('etsy_product.id'))
    product = relationship("EtsyProduct", uselist=False, back_populates='offerings')

    @classmethod
    def create(cls, offering_data: Union[EtsyOffering, Dict[str, Any]],
               product: EtsyProduct = None) -> EtsyOffering:
        if not isinstance(offering_data, EtsyOfferingSpace):
            offering_data = cls.create_namespace(offering_data)

        offering = cls(
            offering_id=offering_data.offering_id,
            quantity=offering_data.quantity,
            is_enabled=offering_data.is_enabled,
            is_deleted=offering_data.is_deleted,
            price=offering_data.price
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
            EtsyOffering.offering_id == offering_id
        ).first()

    def update(self, offering_data: Union[EtsyOffering, Dict[str, Any]],
               product: EtsyProduct = None):
        if not isinstance(offering_data, EtsyOfferingSpace):
            offering_data = self.create_namespace(offering_data)

        self.offering_id = offering_data.offering_id,
        self.quantity = offering_data.quantity,
        self.is_enabled = offering_data.is_enabled,
        self.is_deleted = offering_data.is_deleted,
        self.price = offering_data.price

        if product is not None:
            self.product = product


def create_database():
    engine = make_engine()
    Base.metadata.create_all(engine)
