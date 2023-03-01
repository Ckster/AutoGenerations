from __future__ import annotations
from typing import List, Union, Dict, Any
from database.utils import Base, make_engine
from database.enums import Prodigi
from database.etsy_tables import Address
from database.namespaces import ProdigiOrderSpace, ProdigiChargeSpace, ProdigiShipmentSpace, ProdigiShipmentItemSpace,\
    ProdigiFulfillmentLocationSpace, ProdigiRecipientSpace, ProdigiItemSpace, ProdigiCostSpace, ProdigiAssetSpace,\
    ProdigiPackingSlipSpace, ProdigiChargeItemSpace, ProdigiStatusSpace, ProdigiIssueSpace, \
    ProdigiAuthorizationDetailsSpace

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Float, ForeignKey, Enum, Table, DateTime


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
    items = relationship("ProdigiItem", back_populates="order")
    _packing_slip_id = Column(Integer, ForeignKey('prodigi_packing_slip.id'))
    packing_slip = relationship("ProdigiPackingSlip", uselist=False, back_populates="order")
    _etsy_receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
    etsy_receipt = relationship("EtsyReceipt", back_populates="prodigi_order")

    @classmethod
    def create(cls, order_data: Union[ProdigiOrderSpace, Dict[str, Any]],
               status: ProdigiStatus = None,
               charges: List[ProdigiCharge] = None,
               shipments: List[ProdigiShipment] = None,
               recipient: ProdigiRecipient = None,
               items: List[ProdigiItem] = None,
               packing_slip: ProdigiPackingSlip = None) -> ProdigiOrder:
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

        return order

    @staticmethod
    def create_namespace(order_data: Dict[str, Any]) -> ProdigiOrderSpace:
        return ProdigiOrderSpace(order_data)


class ProdigiShipmentDetail(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#update-shipping-method
    """
    __tablename__ = 'prodigi_shipment_detail'
    id = Column(Integer, primary_key=True)
    prodigi_shipment_id = Column(String)
    successful = Column(Boolean)
    errorCode = Column(Enum(Prodigi.ShipmentUpdateErrorCode))
    description = Column(String)

    # relationships
    _shipment_id = Column(Integer, ForeignKey('prodigi_shipment.id'))
    shipment = relationship("ProdigiShipment", uselist=False, back_populates="updates")


class ProdigiPackingSlip(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-packing-slip
    """
    __tablename__ = 'prodigi_packing_slip'
    id = Column(Integer, primary_key=True)
    url = Column(String)
    status = Column(String)

    # relationships
    order = relationship("ProdigiOrder", back_populates="packing_slip")

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
    _order_id = Column(Integer, ForeignKey('prodigi_order.id'))
    order = relationship("ProdigiOrder", uselist=False, back_populates='items')
    _recipient_cost_id = Column(Integer, ForeignKey('prodigi_cost.id'))
    recipient_cost = relationship("ProdigiCost", uselist=False, back_populates='item')
    assets: Mapped[List[ProdigiAsset]] = relationship(
        secondary=item_asset_association_table, back_populates='items')

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


class ProdigiAsset(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-asset
    """
    __tablename__ = 'prodigi_asset'
    id = Column(Integer, primary_key=True)
    print_area = Column(String)
    url = Column(String)

    # relationships
    items: Mapped[List[ProdigiItem]] = relationship(
        secondary=item_asset_association_table, back_populates='assets')

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
    fulfillment_location = relationship("ProdigiFulfillmentLocation", uselist=False, back_populates="shipment")

    @classmethod
    def create(cls, shipment_data: Union[ProdigiShipmentSpace, Dict[str, Any]],
               order: List[ProdigiOrder] = None,
               items: List[ProdigiItem] = None,
               fulfillment_location: ProdigiFulfillmentLocation = None) -> ProdigiShipment:
        if not isinstance(shipment_data, ProdigiShipmentSpace):
            shipment_data = cls.create_namespace(shipment_data)

        shipment = cls(
            prodigi_id=shipment_data.prodigi_id,
            carrier=shipment_data.carrier,
            tracking=shipment_data.tracking,
            dispatch_date=shipment_data.dispatch_date
        )

        if order is not None:
            shipment.order = order

        if items is not None:
            shipment.items = items

        if fulfillment_location is not None:
            shipment.fulfillment_location = fulfillment_location

        return shipment

    @staticmethod
    def create_namespace(order_data: Dict[str, Any]) -> ProdigiOrderSpace:
        return ProdigiOrderSpace(order_data)


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

    @classmethod
    def create(cls, charge_data: Union[ProdigiChargeSpace, Dict[str, Any]],
               order: ProdigiOrder = None,
               total_cost: ProdigiCost = None,
               items: List[ProdigiItem] = None) -> ProdigiCharge:
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

        if items is not None:
            charge.items = items

        return charge

    @staticmethod
    def create_namespace(charge_data: Dict[str, Any]) -> ProdigiChargeSpace:
        return ProdigiChargeSpace(charge_data)


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
    _authorization_details_id = Column(Integer, ForeignKey('prodigi_authorization_details.id'))
    authorization_details = relationship("ProdigiAuthorizationDetail", uselist=False, back_populates='issues')

    @classmethod
    def create(cls, issue_data: Union[ProdigiIssueSpace, Dict[str, Any]],
               status: ProdigiStatus = None,
               authorization_details: ProdigiAuthorizationDetail = None
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


class ProdigiAuthorizationDetail(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#status-status-authorisation-details
    """
    __tablename__ = 'prodigi_authorization_details'
    id = Column(Integer, primary_key=True)
    authorization_url = Column(String)

    # relationships
    issues = relationship("ProdigiIssue", back_populates="authorization_details")
    payment_details = relationship("ProdigiCost", uselist=False, back_populates="authorization")

    @classmethod
    def create(cls, authorization_detail_data: Union[ProdigiAuthorizationDetailsSpace, Dict[str, Any]],
               issues: List[ProdigiIssue] = None,
               payment_details: List[ProdigiCost] = None
               ) -> ProdigiAuthorizationDetail:
        if not isinstance(authorization_detail_data, ProdigiAuthorizationDetail):
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
    def create_namespace(authorization_detail_data: Dict[str, Any]) -> ProdigiAuthorizationDetail:
        return ProdigiAuthorizationDetail(authorization_detail_data)


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
    authorization = relationship("ProdigiAuthorizationDetail", back_populates="payment_details")
    _charge_id = Column(Integer, ForeignKey('prodigi_charge.id'))
    charge = relationship("ProdigiCharge", back_populates="total_cost")
    _charge_item_id = Column(Integer, ForeignKey('prodigi_charge_item.id'))
    charge_item = relationship("ProdigiChargeItem", back_populates="cost")
    _item_id = Column(Integer, ForeignKey('prodigi_item.id'))
    item = relationship("ProdigiItem", back_populates="recipient_cost")

    @classmethod
    def create(cls, cost_data: Union[ProdigiCostSpace, Dict[str, Any]],
               authorization: ProdigiAuthorizationDetail = None,
               charge: ProdigiCharge = None,
               charge_item: ProdigiChargeItem = None,
               item: ProdigiItem = None
               ) -> ProdigiCost:
        if not isinstance(cost_data, ProdigiCostSpace):
            cost_data = cls.create_namespace(cost_data)

        cost = cls(
            amount=cost_data.amount,
            curreny=cost_data.currency
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
