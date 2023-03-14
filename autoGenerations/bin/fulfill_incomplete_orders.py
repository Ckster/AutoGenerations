import os
import json

from database.namespaces import ProdigiOrderSpace, ProdigiChargeSpace, ProdigiShipmentSpace, ProdigiShipmentItemSpace, \
    ProdigiFulfillmentLocationSpace, ProdigiRecipientSpace, ProdigiItemSpace, ProdigiCostSpace, ProdigiAssetSpace, \
    ProdigiPackingSlipSpace, ProdigiStatusSpace, ProdigiAuthorizationDetailsSpace, ProdigiIssueSpace, \
    ProdigiChargeItemSpace, ProdigiAddressSpace
from database.utils import make_engine
from database.tables import ProdigiOrder, ProdigiStatus, ProdigiCharge, ProdigiCost, ProdigiShipment, \
    ProdigiItem, ProdigiRecipient, ProdigiPackingSlip, ProdigiShipmentItem, ProdigiFulfillmentLocation, ProdigiAsset, \
    ProdigiIssue, ProdigiAuthorizationDetails, ProdigiChargeItem, EtsyReceipt, Address
from database.enums import Prodigi, OrderStatus, Etsy
from apis.prodigi import API
from alerts.email import send_mail

from sqlalchemy.orm import Session


PROJECT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))


def fulfill_orders():
    prodigy_api = API()

    with open(os.path.join(PROJECT_DIR, 'sku_map.json'), 'r') as f:
        sku_map = json.load(f)

    with Session(make_engine()) as session:

        # Receipts will become complete when all transactions for that receipt have been completed
        unfulfilled_paid_receipts = session.query(EtsyReceipt).filter(
            EtsyReceipt.order_status == OrderStatus.INCOMPLETE
        ).filter(
            EtsyReceipt.needs_fulfillment
        ).filter(
            EtsyReceipt.status == Etsy.OrderStatus.PAID
        ).all()

        print(f'Fulfilling {len(unfulfilled_paid_receipts)} orders')

        for receipt in unfulfilled_paid_receipts:
            items_to_order = []
            for transaction in receipt.transactions:

                etsy_sku = transaction.product.sku
                prodigi_sku = sku_map[etsy_sku]['prodigi_sku']
                asset_url = sku_map[etsy_sku]['asset_url']

                items_to_order.append({
                    "sku": prodigi_sku,
                    "copies": transaction.quantity,
                    "sizing": "fillPrintArea",
                    "assets": [
                        {
                            "printArea": "default",
                            "url": asset_url
                        }
                    ]
                })

            if not items_to_order:
                continue

            order_response = prodigy_api.create_order(receipt.address, transaction, items_to_order,
                                                      idempotency_key=receipt.receipt_id)
            outcome = order_response['outcome']

            if outcome.lower() == Prodigi.CreateOrderOutcome.CREATED.value:

                # Order was successful so receipt no longer needs fulfillment
                receipt.needs_fulfillment = False

                prodigi_order_space = ProdigiOrderSpace(order_response['order'])

                # Create the charges
                charges = []
                for charge_dict in prodigi_order_space.charges:
                    charge_space = ProdigiChargeSpace(charge_dict)

                    charge_items = []
                    for charge_item_dict in charge_space.items:
                        charge_item_space = ProdigiChargeItemSpace(charge_item_dict)
                        charge_item = ProdigiChargeItem.create(charge_item_space)
                        session.add(charge_item)
                        session.flush()
                        charge_items.append(charge_item)

                    cost = None
                    if charge_space.total_cost is not None:
                        cost_space = ProdigiCostSpace(charge_space.total_cost)
                        cost = ProdigiCost.create(cost_space)

                    charge = ProdigiCharge.create(charge_space, charge_items=charge_items, total_cost=cost)
                    session.add(charge)
                    charges.append(charge)

                # Create shipments
                shipments = []
                for shipment_dict in prodigi_order_space.shipments:
                    shipment_space = ProdigiShipmentSpace(shipment_dict)

                    shipment_items = []
                    for shipment_item_dict in shipment_space.items:
                        shipment_item_space = ProdigiShipmentItemSpace(shipment_item_dict)
                        shipment_item = ProdigiShipmentItem.create(shipment_item_space)
                        session.add(shipment_item)
                        shipment_items.append(shipment_item)

                    fulfillment_location_space = ProdigiFulfillmentLocationSpace(
                        shipment_space.fulfillment_location)
                    fulfillment_location = ProdigiFulfillmentLocation.create(fulfillment_location_space)

                    shipment = ProdigiShipment.create(shipment_space, shipment_items=shipment_items,
                                                      fulfillment_location=fulfillment_location)
                    session.add(shipment)
                    shipments.append(shipment)

                # Create items
                items = []
                for item_dict in prodigi_order_space.items:
                    item_space = ProdigiItemSpace(item_dict)

                    assets = []
                    for asset_dict in item_space.assets:
                        asset_space = ProdigiAssetSpace(asset_dict)
                        asset = ProdigiAsset.get_existing(session, asset_space)
                        if asset is None:
                            asset = ProdigiAsset.create(asset_space)
                            session.add(asset)
                            session.flush()
                        assets.append(asset)

                    cost = None
                    if item_space.recipient_cost is not None:
                        cost_space = ProdigiCostSpace(item_space.recipient_cost)
                        cost = ProdigiCost.create(cost_space)

                    item = ProdigiItem.create(item_space, assets=assets, recipient_cost=cost)
                    session.add(item)
                    items.append(item)

                # Create the status object
                status_space = ProdigiStatusSpace(prodigi_order_space.status)
                issues = []
                for issue_dict in status_space.issues:
                    authorization_space = ProdigiAuthorizationDetailsSpace(issue_space.authorization_details)
                    authorization = ProdigiAuthorizationDetails.create(authorization_space)

                    issue_space = ProdigiIssueSpace(issue_dict)
                    issue = ProdigiIssue.create(issue_space, authorization_details=authorization)
                    session.add(issue)
                    issues.append(issue)

                status = ProdigiStatus.create(status_space, issues=issues)

                # Create recipient
                recipient_space = ProdigiRecipientSpace(prodigi_order_space.recipient)

                address_space = ProdigiAddressSpace(recipient_space.address)
                address = Address.get_existing(session, address_space.zip, address_space.city, address_space.state,
                                               address_space.country, address_space.first_line,
                                               address_space.second_line)
                if address is None:
                    address = Address.create(address_space)
                    session.add(address)
                    session.flush()

                recipient = ProdigiRecipient.get_existing(session, recipient_space)
                if recipient is None:
                    recipient = ProdigiRecipient.create(recipient_space, addresses=[address])
                    session.add(recipient)
                    session.flush()
                else:
                    recipient.update(recipient_space, addresses=[address])

                # Create packing slip
                packing_slip = None
                if prodigi_order_space.packing_slip is not None:
                    packing_slip_space = ProdigiPackingSlipSpace(prodigi_order_space.packing_slip)
                    packing_slip = ProdigiPackingSlip.create(packing_slip_space)
                    session.add(packing_slip)

                # Create the order object
                prodigi_order = ProdigiOrder.create(prodigi_order_space, status=status, recipient=recipient,
                                                    packing_slip=packing_slip, charges=charges, shipments=shipments,
                                                    items=items)
                session.add(prodigi_order)
                receipt.update(prodigi_orders=[prodigi_order])

            else:
                error_string = f"For Etsy receipt id: {receipt.receipt_id} \nProdigi Outcome: {outcome}"
                send_mail('Prodigi Order Creation Error', error_string)

            session.commit()


if __name__ == '__main__':
    try:
        fulfill_orders()
    except Exception as e:
        send_mail('Fulfill Orders Error', str(e))
