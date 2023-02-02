from __future__ import annotations
from typing import List, Union, Dict, Any
from database.utils import Base, make_engine
from database.enums import Etsy
from database.namespaces import EtsyReceiptSpace, EtsyReceiptShipmentSpace, EtsySellerSpace, EtsyBuyerSpace,\
    EtsyTransactionSpace, AddressSpace, EtsyProductPropertySpace, EtsyProductSpace

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, ForeignKey, Enum, ARRAY, Table


transaction_product_data_association_table = Table(
    "transaction_product_data_association_table",
    Base.metadata,
    Column("transaction_id", ForeignKey("etsy_transaction.id"), primary_key=True),
    Column("product_data_id", ForeignKey("etsy_product_property.id"), primary_key=True)
)


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

    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship("Address", uselist=False, back_populates='receipts')
    buyer_id = Column(Integer, ForeignKey('etsy_buyer.id'))
    buyer = relationship("EtsyBuyer", uselist=False, back_populates='receipts')
    seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates='receipts')

    transactions = relationship("EtsyTransaction", back_populates='receipt')
    receipt_shipments = relationship("EtsyReceiptShipment", back_populates='receipt')

    @classmethod
    def create(cls, receipt_data: Union[EtsyReceiptSpace, Dict[str, Any]], address: Address, buyer: EtsyBuyer,
               seller: EtsySeller, transactions: List[EtsyTransaction],
               receipt_shipments: List[EtsyReceiptShipment]) -> EtsyReceipt:
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
            gift_wrap_price=receipt_data.gift_wrap_price,
            address=address,
            buyer=buyer,
            seller=seller
        )

        if transactions:
            print(transactions)
            receipt.transactions = transactions
        if receipt_shipments:
            receipt.receipt_shipments = receipt_shipments

        return receipt

    @staticmethod
    def create_namespace(etsy_receipt: Dict[str, Any]):
        return EtsyReceiptSpace(etsy_receipt)

    @staticmethod
    def get_existing(session, receipt_data: Union[EtsyReceiptSpace, Dict[str, Any]]):
        if not isinstance(receipt_data, EtsyReceiptSpace):
            receipt_data = EtsyReceipt.create_namespace(receipt_data)

        return session.query(EtsyReceipt).filter(EtsyReceipt.receipt_id == receipt_data.receipt_id).first()


class EtsySeller(Base):
    __tablename__ = 'etsy_seller'
    id = Column(Integer, primary_key=True)
    seller_id = Column(Integer, unique=True)
    email = Column(String)

    receipts = relationship('EtsyReceipt', back_populates='seller')
    transactions = relationship("EtsyTransaction", back_populates='seller')

    @classmethod
    def create(cls, seller_data: Union[EtsySellerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None,
               transactions: List[EtsyTransaction] = None) -> EtsySeller:
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

        return seller

    @staticmethod
    def create_namespace(seller_data: Dict[str, Any]):
        return EtsySellerSpace(seller_data)

    @staticmethod
    def get_existing(session, seller_id: int):
        return session.query(EtsySeller).filter(
            EtsySeller.seller_id == seller_id
        ).first()

    def update(self, seller_data: Union[EtsySellerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None, transactions: List[EtsyTransaction] = None,
               overwrite_list: bool = False):
        if not isinstance(seller_data, EtsySellerSpace):
            seller_data = self.create_namespace(seller_data)
        self.email = seller_data.email

        if receipts is not None:
            self.receipts = receipts if overwrite_list else self.receipts + receipts

        if transactions:
            self.transactions = transactions if overwrite_list else self.transactions + transactions


class EtsyBuyer(Base):
    __tablename__ = 'etsy_buyer'
    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, unique=True)
    email = Column(String)

    receipts = relationship('EtsyReceipt', back_populates='buyer')
    transactions = relationship("EtsyTransaction", back_populates='buyer')

    @classmethod
    def create(cls, buyer_data: Union[EtsyBuyerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None,
               transactions: List[EtsyTransaction] = None) -> EtsyBuyer:
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
    def get_existing(session, buyer_id: int):
        return session.query(EtsyBuyer).filter(
            EtsyBuyer.buyer_id == buyer_id
        ).first()

    def update(self, buyer_data: Union[EtsyBuyerSpace, Dict[str, Any]],
               receipts: List[EtsyReceipt] = None, transactions: List[EtsyTransaction] = None,
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
    zip = Column(String)
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
            zip=address_data.zip,
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
    def get_existing(session, address_data: Union[AddressSpace, Dict[str, Any]]):
        if not isinstance(address_data, AddressSpace):
            address_data = Address.create_namespace(address_data)

        return session.query(Address).filter(
            Address.zip == address_data.zip,
            Address.city == address_data.city,
            Address.state == address_data.state,
            Address.country == address_data.country,
            Address.first_line == address_data.first_line,
            Address.second_line == address_data.second_line
        ).first()


class EtsyTransaction(Base):
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
    etsy_product_id = Column(BigInteger)

    shipping_profile_id = Column(Integer, ForeignKey('etsy_shipping_profile.id'))
    shipping_profile = relationship('EtsyShippingProfile', uselist=False, back_populates='transactions')
    receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
    receipt = relationship('EtsyReceipt', uselist=False, back_populates='transactions')
    buyer_id = Column(Integer, ForeignKey('etsy_buyer.id'))
    buyer = relationship('EtsyBuyer', uselist=False, back_populates='transactions')
    seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship('EtsySeller', uselist=False, back_populates='transactions')
    product_id = Column(Integer, ForeignKey('etsy_product.id'))
    product = relationship('EtsyProduct', uselist=False, back_populates='transactions')

    # Many to Many relationship
    product_properties: Mapped[List[EtsyProductProperty]] = relationship(
        secondary=transaction_product_data_association_table, back_populates='transactions')

    @classmethod
    def create(cls, transaction_data: Union[EtsyTransactionSpace, Dict[str, Any]], buyer: EtsyBuyer,
               seller: EtsySeller, existing_product: EtsyProduct,
               product_properties: List[EtsyProductProperty]) -> EtsyTransaction:
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
            etsy_product_id=transaction_data.product_id,
            buyer_id=buyer.id,
            seller_id=seller.id,
            product_id=existing_product.id,
            product_properties=product_properties
        )

        return transaction

    @staticmethod
    def create_namespace(etsy_transaction: Dict[str, Any]):
        return EtsyTransactionSpace(etsy_transaction)

    @staticmethod
    def get_existing(session, transaction_data: Union[EtsyTransactionSpace, Dict[str, Any]]):
        if not isinstance(transaction_data, EtsyTransactionSpace):
            transaction_data = EtsyTransaction.create_namespace(transaction_data)

        return session.query(EtsyTransaction).filter(
                    EtsyTransaction.transaction_id == transaction_data.transaction_id
                ).first()


class EtsyProduct(Base):
    __tablename__ = 'etsy_product'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, unique=True)
    sku = Column(Integer)
    price = Column(Float)

    transactions = relationship("EtsyTransaction", back_populates='product')

    @classmethod
    def create(cls, product_data: Union[EtsyProductSpace, Dict[str, Any]],
               transactions: List[EtsyTransaction] = None) -> EtsyProduct:
        if not isinstance(product_data, EtsyProductSpace):
            product_data = cls.create_namespace(product_data)

        product = cls(
            product_id=product_data.product_id,
            sku=product_data.sku,
            price=product_data.price
        )

        if transactions is not None:
            product.transactions = transactions

        return product

    @staticmethod
    def create_namespace(product_data: Dict[str, Any]):
        return EtsyProductSpace(product_data)

    @staticmethod
    def get_existing(session, product_id: int):
        return session.query(EtsyProduct).filter(EtsyProduct.product_id == product_id).first()


class EtsyShippingProfile(Base):
    __tablename__ = 'etsy_shipping_profile'
    id = Column(Integer, primary_key=True)
    shipping_profile_id = Column(Integer, unique=True)
    name = Column(String)

    transactions = relationship("EtsyTransaction", back_populates='shipping_profile')


class EtsyReceiptShipment(Base):
    __tablename__ = 'etsy_shipment'
    id = Column(Integer, primary_key=True)
    receipt_shipping_id = Column(BigInteger, unique=True)
    shipment_notification_timestamp = Column(BigInteger)
    carrier_name = Column(String)
    tracking_code = Column(String)

    receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
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
    def get_existing(session, shipment_data: Union[EtsyReceiptShipment,
                                                   Dict[str, Any]]) -> Union[None, EtsyReceiptShipment]:
        if not isinstance(shipment_data, EtsyReceiptShipmentSpace):
            shipment_data = EtsyReceipt.create_namespace(shipment_data)

        return session.query(EtsyReceiptShipment).filter(
            EtsyReceiptShipment.receipt_id == shipment_data.receipt_id
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
    property_id = Column(Integer, unique=True)
    formatted_name = Column(String)
    formatted_value = Column(String)


class EtsyProductProperty(Base):
    __tablename__ = 'etsy_product_property'
    id: Mapped[int] = mapped_column(primary_key=True)

    property_id = Column(BigInteger, unique=True)
    property_name = Column(String)
    scale_id = Column(BigInteger)
    scale_name = Column(String)

    transactions: Mapped[List[EtsyTransaction]] = relationship(
        secondary=transaction_product_data_association_table, back_populates="product_properties"
    )

    @classmethod
    def create(cls, property_data: Union[EtsyProductPropertySpace, Dict[str, Any]],
               transactions: List[EtsyTransaction] = None) -> EtsyProductProperty:
        if not isinstance(property_data, EtsyProductPropertySpace):
            property_data = cls.create_namespace(property_data)

        property_data = cls(
            product_id=property_data.property_id,
            property_name=property_data.property_name,
            scale_id=property_data.scale_id,
            scale_name=property_data.scale_name
        )

        if transactions is not None:
            property_data.transactions = transactions

        return property_data

    @staticmethod
    def create_namespace(property_data: Dict[str, Any]):
        return EtsyProductPropertySpace(property_data)

    @staticmethod
    def get_existing(session, property_data: Union[EtsyProductPropertySpace,
                                                   Dict[str, Any]]) -> Union[None, EtsyProductProperty]:
        if not isinstance(property_data, EtsyProductPropertySpace):
            property_data = EtsyReceipt.create_namespace(property_data)

        return session.query(EtsyProductProperty).filter(
            EtsyProductProperty.property_id == property_data.property_id
        ).filter(
            EtsyProductProperty.property_name == property_data.property_name
        ).first()

    def update(self, property_data: Union[EtsyProductPropertySpace, Dict[str, Any]],
               transactions: List[EtsyTransaction] = None,
               overwrite_lists: bool = False):
        if not isinstance(property_data, EtsyProductPropertySpace):
            property_data = self.create_namespace(property_data)

        self.product_id = property_data.property_id
        self.property_name = property_data.property_name
        self.scale_id = property_data.scale_id
        self.scale_name = property_data.scale_name

        if transactions is not None:
            self.transactions = transactions if overwrite_lists else self.transactions + transactions


def create_database():
    engine = make_engine()
    Base.metadata.create_all(engine)
