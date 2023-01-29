from database.utils import Base, make_engine
from database.enums import Etsy

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, ForeignKey, Enum


class EtsyReceipt(Base):
    """
    API Reference: https://developer.etsy.com/documentation/reference#operation/getShopReceipt
    """
    __tablename__ = 'etsy_receipt'
    id = Column(Integer, primary_key=True)
    receipt_id = Column(Integer)
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
    gift_messsage = Column(String)
    grand_total = Column(Float)
    sub_total = Column(Float)
    total_price = Column(Float)
    shipping_cost = Column(Float)
    tax_cost = Column(Float)
    vat_cost = Column(Float)
    discount = Column(Float)

    address_id = Column(Integer, ForeignKey('address.id'))
    address = relationship("Address", uselist=False, back_populates='receipts')
    buyer_id = Column(Integer, ForeignKey('etsy_buyer.id'))
    buyer = relationship("EtsyBuyer", uselist=False, back_populates='receipts')
    seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship("EtsySeller", uselist=False, back_populates='receipts')

    transactions = relationship("Transactions", back_populates='receipts')


class EtsySeller(Base):
    __tablename__ = 'etsy_seller'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    email = Column(String)
    name = Column(String)

    receipts = relationship('EtsyReceipt', back_populates='seller')
    transactions = relationship("EtsyTransaction", back_populates='seller')


class EtsyBuyer(Base):
    __tablename__ = 'etsy_buyer'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, primary_key=True)
    email = Column(String)
    name = Column(String)

    receipts = relationship('EtsyReceipt', back_populates='seller')
    transactions = relationship("EtsyTransaction", back_populates='buyer')


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


class EtsyTransaction(Base):
    __tablename__ = 'etsy_transaction'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    create_timestamp = Column(BigInteger)
    paid_timestamp = Column(BigInteger)
    shipped_timestamp = Column(BigInteger)
    quantity = Column(Integer)
    is_digital = Column(Boolean)
    file_data = Column(String)
    transaction_type = Column(String)
    shipping_cost = Column(Float)
    min_processing_days = Column(Integer)
    max_processing_days = Column(Integer)
    shipping_method = Column(String)
    shipping_upgrade = Column(String)
    expected_ship_date = Column(BigInteger)
    buyer_coupon = Column(Integer)
    shop_coupon = Column(Integer)

    receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
    receipt = relationship('EtsyReceipt', uselist=False, back_populates='transactions')
    buyer_id = Column(Integer, ForeignKey('etsy_buyer.id'))
    buyer = relationship('EtsyBuyer', uselist=False, back_populates='transactions')
    seller_id = Column(Integer, ForeignKey('etsy_seller.id'))
    seller = relationship('EtsySeller', uselist=False, back_populates='transactions')
    product_id = Column(Integer, ForeignKey('etsy_product.id'))
    product = relationship('EtsyProduct', uselist=False, back_populates='transactions')
    shipping_profile_id = Column(Integer, ForeignKey('etsy_shipping_profile.id'))
    shipping_profile = relationship('EtsyShippingProfile', uselist=False, back_populates='transactions')


class EtsyProduct(Base):
    __tablename__ = 'etsy_product'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    sku = Column(Integer)
    price = Column(Float)

    transactions = relationship("EtsyTransaction", back_populates='product')


class EtsyShippingProfile(Base):
    __tablename__ = 'etsy_shipping_profile'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    transactions = relationship("EtsyTransaction", back_populates='shipping_profile')


def create_database():
    engine = make_engine()
    Base.metadata.create_all(engine)