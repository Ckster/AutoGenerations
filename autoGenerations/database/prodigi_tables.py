from __future__ import annotations
from typing import List, Union, Dict, Any
from database.utils import Base, make_engine
from database.enums import Prodigi
from database.etsy_tables import Address

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, ForeignKey, Enum, Table, DateTime


recipient_address_association_table = Table(
    "recipient_address_association_table",
    Base.metadata,
    Column("recipient_id", ForeignKey("prodigi_recipient.id"), primary_key=True),
    Column("address_id", ForeignKey("address.id"), primary_key=True)
)


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
    status = relationship("ProdigiStatus", uselist=False, back_populates='order')
    charges = relationship("ProdigiCharge", back_populates="order")
    shipments = relationship("ProdigiShipment", back_populates="order")
    _recipient_id = Column(Integer, ForeignKey('prodigi_recipient.id'))
    recipient = relationship("ProdigiRecipient", uselist=False, back_populates="orders")
    items = relationship()
    packing_slip = relationship()

    # TODO: Not sure about this
    metadata = relationship()


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
    orders = relationship("ProdigiOrder", back_populates="recipient")
    addresses: Mapped[List[Address]] = relationship(
        secondary=recipient_address_association_table, back_populates='prodigi_recipients')


class ProdigiShipment(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-shipment
    """
    __tablename__ = 'prodigi_shipment'
    id = Column(Integer, primary_key=True)
    prodigi_id = Column(String, unique=True)
    carrier = Column(String)
    tracking = Column(String)
    dispatch_date = Column(DateTime)

    # relationships
    _order_id = Column(Integer, ForeignKey('prodigi_order.id'))
    order = relationship("ProdigiOrder", uselist=False, back_populates="shipments")
    items = relationship("ProdigiShipmentItem", back_populates='shipment')
    _fulfillment_location_id = Column(Integer, ForeignKey('prodigi_shipment.id'))
    fulfillment_location = relationship()


class ProdigiFulfillmentLocation(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-fulfillment-location
    """
    __tablename__ = 'prodigi_shipment'
    id = Column(Integer, primary_key=True)
    country_code = Column(String)
    lab_code = Column(String)

    # relationships
    shipment = relationship("ProdigiShipment", back_populates="fulfillment_location")


class ProdigiShipmentItem(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-shipment-item
    """
    __tablename__ = 'prodigi_shipment_item'
    id = Column(Integer, primary_key=True)
    item_id = Column(String, unique=True)

    # relationships
    _shipment_id = Column(Integer, ForeignKey('prodigi_shipment.id'))
    shipment = relationship("ProdigiShipment", uselist=False, back_populates='items')


class ProdigiCharge(Base):
    __tablename__ = 'prodigi_charge'
    id = Column(Integer, primary_key=True)
    prodigi_id = Column(String, unique=True)
    prodigi_invoice_number = Column(String)

    # relationships
    _order_id = Column(Integer, ForeignKey('prodigi_order.id'))
    order = relationship("ProdigiOrder", uselist=False, back_populates="charges")
    total_cost = relationship("ProdigiCost", uselist=False, back_populates="charge")
    items = relationship("ProdigiChargeItem", back_populates="charge")


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
    cost = relationship("ProdigiCost", uselist=False, back_populates="charge_item")
    _charge_id = Column(Integer, ForeignKey('prodigi_charge.id'))
    charge = relationship("ProdigiCharge", uselist=False, back_populates="items")


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
    _order_id = Column(Integer, ForeignKey('prodigi_order.id'))
    order = relationship("ProdigiOrder", back_populates="status")
    issues = relationship("ProdigiIssue", back_populates="status")


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
    _status_id = Column(Integer, ForeignKey('prodigi_status.id'))
    status = relationship("ProdigiStatus", uselist=False, back_populates="issues")
    authorization_details = relationship()


class ProdigiAuthorizationDetails(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#status-status-authorisation-details
    """
    __tablename__ = 'prodigi_authorization_details'
    id = Column(Integer, primary_key=True)
    authorization_url = Column(String)

    # relationships
    payment_details = relationship("ProdigiCost", uselist=False, back_populates="authorization")


class ProdigiCost(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object
    """
    __tablename__ = 'prodigi_cost'
    id = Column(Integer, primary_key=True)
    amount = Column(String)
    currency = Column(String)

    # relationships
    _authorization_id = Column(Integer, ForeignKey('prodigi_authorization_details.id'))
    authorization = relationship("ProdigiAuthorizationDetails", back_populates="payment_details")
    _charge_id = Column(Integer, ForeignKey('prodigi_charge.id'))
    charge = relationship("ProdigiCharge", back_populates="total_cost")
    _charge_item_id = Column(Integer, ForeignKey('prodigi_charge_item.id'))
    charge_item = relationship("ProdigiChargeItem", back_populates="cost")