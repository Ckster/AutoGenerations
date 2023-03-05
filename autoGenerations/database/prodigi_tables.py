from __future__ import annotations
from typing import List, Union, Dict, Any
from database.utils import Base
from database.enums import Prodigi
from database.etsy_tables import Address, merge_lists, EtsyReceipt
from database.namespaces import ProdigiOrderSpace, ProdigiChargeSpace, ProdigiShipmentSpace, ProdigiShipmentItemSpace,\
    ProdigiFulfillmentLocationSpace, ProdigiRecipientSpace, ProdigiItemSpace, ProdigiCostSpace, ProdigiAssetSpace,\
    ProdigiPackingSlipSpace, ProdigiChargeItemSpace, ProdigiStatusSpace, ProdigiIssueSpace, \
    ProdigiAuthorizationDetailsSpace, ProdigiShipmentDetailSpace

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

    # one to many
    charges = relationship("ProdigiCharge", back_populates="order", cascade="all, delete, delete-orphan")
    shipments = relationship("ProdigiShipment", back_populates="order", cascade="all, delete, delete-orphan")
    items = relationship("ProdigiItem", back_populates="order", cascade="all, delete, delete-orphan")

    # many to one
    _recipient_id = Column(Integer, ForeignKey('prodigi_recipient.id'))
    recipient = relationship("ProdigiRecipient", uselist=False, back_populates="orders")
    _etsy_receipt_id = Column(Integer, ForeignKey('etsy_receipt.id'))
    etsy_receipt = relationship("EtsyReceipt", uselist=False, back_populates="prodigi_order")

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
    shipment = relationship("ProdigiShipment", uselist=False, back_populates="updates")

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
    assets: Mapped[List[ProdigiAsset]] = relationship(secondary=item_asset_association_table, back_populates='items',
                                                      cascade='all, delete-orphan')

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

    def update(self, asset_data: Union[ProdigiAssetSpace, Dict[str, Any]],
               items: List[ProdigiItem] = None,
               overwrite_list: bool = False
               ):
        if not isinstance(asset_data, ProdigiAssetSpace):
            asset_data = self.create_namespace(asset_data)

        if self.print_area != asset_data.print_area:
            self.print_area = asset_data.print_area
        if self.url != asset_data.url:
            self.url = asset_data.url

        if items is not None:
            self.items = items if overwrite_list else merge_lists(self.items, items)


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
        secondary=recipient_address_association_table, back_populates='prodigi_recipients',
        cascade='all, delete-orphan')

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

    def get_existing(self, session, recipient_data: Union[ProdigiRecipientSpace, Dict[str, Any]]):
        if not isinstance(recipient_data, ProdigiRecipientSpace):
            recipient_data = self.create_namespace(recipient_data)
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
    carrier = Column(String)
    tracking = Column(String)
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
            carrier=shipment_data.carrier,
            tracking=shipment_data.tracking,
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
    def create_namespace(order_data: Dict[str, Any]) -> ProdigiOrderSpace:
        return ProdigiOrderSpace(order_data)

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

        if self.carrier != shipment_data.carrier:
            self.carrier = shipment_data.carrier
        if self.tracking != shipment_data.tracking:
            self.tracking = shipment_data.tracking
        if self.dispatch_date != shipment_data.dispatch_date:
            self.dispatch_date = shipment_data.dispatch_date

        if order is not None and self.order != order:
            self.order = order

        if fulfillment_location is not None and self.fulfillment_location != fulfillment_location:
            self.fulfillment_location = fulfillment_location

        if shipment_items is not None:
            self.shipment_items = shipment_items if overwrite_list else merge_lists(self.items, shipment_items)


class ProdigiFulfillmentLocation(Base):
    """
    API Reference: https://www.prodigi.com/print-api/docs/reference/#order-object-fulfillment-location
    """
    __tablename__ = 'prodigi_shipment'
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
