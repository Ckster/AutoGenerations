from database.namespaces import ProdigiOrderSpace, ProdigiChargeSpace, ProdigiShipmentSpace, ProdigiShipmentItemSpace
from database.utils import make_engine
from database.etsy_tables import EtsyReceipt
from database.prodigi_tables import ProdigiOrder, ProdigiStatus, ProdigiCharge, ProdigiCost, ProdigiShipment,\
    ProdigiItem, ProdigiRecipient, ProdigiPackingSlip, ProdigiShipmentItem, ProdigiFulfillmentLocation, ProdigiAsset
from database.enums import Etsy, Prodigi, OrderStatus, TransactionFulfillmentStatus
from apis.prodigi import API

from sqlalchemy.orm import Session


# TODO: Receipts will become complete when all transactions for that receipt have been completed
def main():
    prodigy_api = API()
    with Session(make_engine()) as session:
        incomplete_receipts = session.query(EtsyReceipt).filter(
            EtsyReceipt.order_status == OrderStatus.INCOMPLETE
        ).all()

        for receipt in incomplete_receipts:

            # TODO: Relate prodigi order to transaction
            items_to_order = []
            for transaction in receipt.transactions:
                if transaction.fulfillment_status == TransactionFulfillmentStatus.NEEDS_FULFILLMENT:
                    # TODO: Append the order item dictionaries here
                    items_to_order.append({})

            order_response = prodigy_api.create_order(receipt.address, transaction)

            if order_response['outcome'] == Prodigi.CreateOrderOutcome.CREATED.value:
                transaction.fulfillment_status = TransactionFulfillmentStatus.IN_PROGRESS
                prodigi_order_space = ProdigiOrderSpace(order_response['order'])

                # Create / update the order object
                prodigi_order = ProdigiOrder.get_existing(prodigi_order_space.prodigi_id)
                if prodigi_order is None:
                    prodigi_order = ProdigiOrder.create(prodigi_order_space)
                    session.add(prodigi_order)
                    session.flush()
                else:
                    prodigi_order.update(prodigi_order_space)

                # Create / update the status object
                status = prodigi_order.status
                if status is None:
                    status = ProdigiStatus.create(prodigi_order_space.status)
                    prodigi_order.status = status
                else:
                    status.update(prodigi_order_space.status)

                charges = []
                for charge_dict in prodigi_order_space.charges:
                    charge_space = ProdigiChargeSpace(charge_dict)
                    charge = ProdigiCharge.get_existing(charge_space.prodigi_id)
                    if charge is None:
                        charge = ProdigiCharge.create(charge_space)
                        session.add(charge)
                        session.flush()
                    else:
                        charge.update(charge_space)

                    # TODO: Pass cost data
                    if charge.cost is None:
                        cost = ProdigiCost.create()
                        charge.cost = cost
                    else:
                        cost.update()

                    charge_items = []
                    for charge_item_dict in charge_space.items:
                        # TODO: Create / add charge items
                        pass

                    charges.append(charge)

                shipments = []
                for shipment_dict in prodigi_order_space.shipments:
                    shipment_space = ProdigiShipmentSpace(shipment_dict)

                    shipment_items = []
                    for shipment_item_dict in shipment_space.items:
                        shipment_item_space = ProdigiShipmentItemSpace(shipment_item_dict)
                        shipment_item = ProdigiShipmentItem.get_existing(shipment_item_space.item_id)
                        if shipment_item is None:
                            shipment_item = ProdigiShipmentItem.create(shipment_item_space)
                            session.add(shipment_item)
                            session.flush()
                        else:
                            shipment_item.update(shipment_item_space)
                        shipment_items.append(shipment_item)

                    fulfillment_location = ProdigiFulfillmentLocation.get_existing(shipment_space.fulfillment_location)
                    fulfillment_location_space = ProdigiFulfillmentLocationSpace(shipment_space.fulfillment_location)
                    if fulfillment_location is None:
                        fulfillment_location = ProdigiFulfillmentLocation.create(fulfillment_location_space)
                        session.add(fulfillment_location)
                        session.flush()
                    else:
                        fulfillment_location.update(fulfillment_location)

                    # TODO: Add above relationships
                    shipment = ProdigiShipment.get_existing(shipment_dict)
                    if shipment is None:
                        shipment = ProdigiShipment.create(shipment_space)
                        session.add(shipment)
                        session.flush()
                    else:
                        shipment.update(shipment_space)
                    shipments.append(shipment)

                recipient = prodigi_order.recipient
                recipient_space = ProdigiRecipientSpace(prodigi_order_space.recipient)
                # TODO: Add the address
                if receipt is None:
                    recipient = ProdigiRecipient.create(recipient_space)
                    session.add(receipt)
                    session.flush()
                else:
                    recipient.update(recipient_space)

                items = []
                for item_dict in prodigi_order_space.items:
                    item_space = ProdigiItemSpace(item_dict)

                    cost_space = ProdigiCostSpace(item_space.recipient_cost)
                    cost = ProdigiCost.get_existing(cost_space)
                    if cost is None:
                        cost = ProdigiCost.create(cost_space)
                    # Nothing to update for cost

                    assets = []
                    for asset_dict in item_space.assets:
                        asset_space = ProdigiAssetSpace(asset_dict)
                        asset = ProdigiAsset.get_existing()
                        if asset is None:
                            asset = ProdigiAsset.create()
                            session.add(asset)
                            session.flush()
                        else:
                            asset.update()
                        assets.append(asset)

                    # TODO: Add cost and assets relationships
                    item = ProdigiItem.get_existing(item_space)
                    if item is None:
                        item = ProdigiItem.create(item_space)
                        session.add(item)
                        session.flush()
                    else:
                        item.update(item_space)
                    items.append(item)

                # TODO: Add packing slip here
                packing_slip = prodigi_order.packing_slip
                packing_slip_space = ProdigiPackingSlipSpace(prodigi_order_space.packing_slip)
                if packing_slip is None:
                    packing_slip = ProdigiPackingSlip.create(packing_slip_space)
                    session.add(packing_slip)
                    session.flush()
                else:
                    packing_slip.update(packing_slip_space)

                # Order was successful so each transaction should be updated to IN_PROGRESS
                for transaction in receipt.transactions:
                    if transaction.fulfillment_status == TransactionFulfillmentStatus.NEEDS_FULFILLMENT:
                        transaction.fulfillment_status = TransactionFulfillmentStatus.IN_PROGRESS

            else:
                pass
                # TODO: Alert about an issue with the order
