from database.namespaces import ProdigiOrderSpace, ProdigiChargeSpace, ProdigiShipmentSpace, ProdigiShipmentItemSpace, \
    ProdigiFulfillmentLocationSpace, ProdigiRecipientSpace, ProdigiItemSpace, ProdigiCostSpace, ProdigiAssetSpace, \
    ProdigiPackingSlipSpace, ProdigiStatusSpace, ProdigiAuthorizationDetailsSpace, ProdigiIssueSpace, \
    ProdigiChargeItemSpace, ProdigiAddressSpace
from database.utils import make_engine
from database.etsy_tables import EtsyReceipt, Address
from database.prodigi_tables import ProdigiOrder, ProdigiStatus, ProdigiCharge, ProdigiCost, ProdigiShipment, \
    ProdigiItem, ProdigiRecipient, ProdigiPackingSlip, ProdigiShipmentItem, ProdigiFulfillmentLocation, ProdigiAsset, \
    ProdigiIssue, ProdigiAuthorizationDetail, ProdigiChargeItem
from database.enums import Prodigi, OrderStatus, TransactionFulfillmentStatus
from apis.prodigi import API
from alerts.email import send_mail

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
            outcome = order_response['outcome']

            if outcome == Prodigi.CreateOrderOutcome.CREATED.value:
                transaction.fulfillment_status = TransactionFulfillmentStatus.IN_PROGRESS
                prodigi_order_space = ProdigiOrderSpace(order_response['order'])

                # Create / update the charges
                charges = []
                for charge_dict in prodigi_order_space.charges:
                    charge_space = ProdigiChargeSpace(charge_dict)

                    charge_items = []
                    for charge_item_dict in charge_space.items:
                        charge_item_space = ProdigiChargeItemSpace(charge_item_dict)
                        charge_item = ProdigiChargeItem.get_existing(charge_item_space)
                        if charge_item is None:
                            charge_item = ProdigiChargeItem.create(charge_item_space)
                            session.add(charge_item)
                            session.flush()
                        else:
                            charge_item.update(charge_item_space)
                        charge_items.append(charge_item)

                    charge = ProdigiCharge.get_existing(charge_space.prodigi_id)
                    if charge is None:
                        charge = ProdigiCharge.create(charge_space, items=charge_items)
                        session.add(charge)
                        session.flush()
                    else:
                        charge.update(charge_space, items=charge_items)

                    cost = charge.cost
                    cost_space = ProdigiCostSpace(charge_space.total_cost)
                    if charge.cost is None:
                        cost = ProdigiCost.create(cost_space)
                        charge.cost = cost
                    else:
                        cost.update(cost_space)

                    charges.append(charge)

                # Create / update shipments
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

                    shipment = ProdigiShipment.get_existing(shipment_dict)
                    if shipment is None:
                        shipment = ProdigiShipment.create(shipment_space, items=shipment_items)
                        session.add(shipment)
                        session.flush()
                    else:
                        shipment.update(shipment_space, items=shipment_items)

                    fulfillment_location = shipment.fulfillment_location
                    fulfillment_location_space = ProdigiFulfillmentLocationSpace(
                        shipment_space.fulfillment_location)
                    if fulfillment_location is None:
                        fulfillment_location = ProdigiFulfillmentLocation.create(fulfillment_location_space)
                        shipment.fulfillment_location = fulfillment_location
                        session.flush()
                    else:
                        fulfillment_location.update(fulfillment_location)

                    shipments.append(shipment)

                # Create / update items
                items = []
                for item_dict in prodigi_order_space.items:
                    item_space = ProdigiItemSpace(item_dict)

                    assets = []
                    for asset_dict in item_space.assets:
                        asset_space = ProdigiAssetSpace(asset_dict)
                        asset = ProdigiAsset.get_existing(asset_space)
                        if asset is None:
                            asset = ProdigiAsset.create(asset_space)
                            session.add(asset)
                            session.flush()
                        else:
                            asset.update(asset_space)
                        assets.append(asset)

                    item = ProdigiItem.get_existing(item_space)
                    if item is None:
                        item = ProdigiItem.create(item_space, assets=assets)
                        session.add(item)
                        session.flush()
                    else:
                        item.update(item_space, assets=assets)

                    cost = item.recipient_cost
                    cost_space = ProdigiCostSpace(item_space.recipient_cost)
                    if cost is None:
                        cost = ProdigiCost.create(cost_space)
                        item.recipient_cost = cost

                    items.append(item)

                # Create / update the order object
                prodigi_order = ProdigiOrder.get_existing(prodigi_order_space.prodigi_id)
                if prodigi_order is None:
                    prodigi_order = ProdigiOrder.create(prodigi_order_space, charges=charges, shipments=shipments,
                                                        items=items)
                    session.add(prodigi_order)
                    session.flush()
                else:
                    prodigi_order.update(prodigi_order_space, charges=charges, shipments=shipments,
                                         items=items)

                # Create / update the status object
                status = prodigi_order.status
                status_space = ProdigiStatusSpace(prodigi_order.status)

                issues = []
                for issue_dict in status_space.issues:
                    issue_space = ProdigiIssueSpace(issue_dict)

                    issue = ProdigiIssue.get_existing(issue_space)
                    if issue is None:
                        issue = ProdigiIssue.create(issue_space)
                        session.add(issue)
                        session.flush()
                    else:
                        issue.update(issue_space)

                    authorization = issue.authorization_details
                    authorization_space = ProdigiAuthorizationDetailsSpace(issue_space.authorization_details)
                    if authorization is None:
                        authorization = ProdigiAuthorizationDetail.create(authorization_space)
                        issue.authorization_details = authorization
                    else:
                        authorization.update(authorization_space)

                    issues.append(issue)

                if status is None:
                    status = ProdigiStatus.create(status_space, issues=issues)
                    prodigi_order.status = status
                else:
                    status.update(prodigi_order_space.status, issues=issues)

                # Create / update recipient
                recipient = prodigi_order.recipient
                recipient_space = ProdigiRecipientSpace(prodigi_order_space.recipient)

                address_space = ProdigiAddressSpace(recipient_space.address)
                address = Address.get_existing(session, address_space.zip, address_space.city, address_space.state,
                                               address_space.country, address_space.first_line,
                                               address_space.second_line)
                if address is None:
                    address = Address.create(address_space)
                    session.add(address)
                    session.flush()

                if receipt is None:
                    recipient = ProdigiRecipient.create(recipient_space, addresses=[address])
                    prodigi_order.recipient = recipient
                    session.flush()
                else:
                    recipient.update(recipient_space, addresses=[address])

                # Create / update packing slip
                packing_slip = prodigi_order.packing_slip
                packing_slip_space = ProdigiPackingSlipSpace(prodigi_order_space.packing_slip)
                if packing_slip is None:
                    packing_slip = ProdigiPackingSlip.create(packing_slip_space)
                    prodigi_order.packing_slip = packing_slip
                    session.flush()
                else:
                    packing_slip.update(packing_slip_space)

                # Order was successful so each transaction should be updated to IN_PROGRESS
                for transaction in receipt.transactions:
                    if transaction.fulfillment_status == TransactionFulfillmentStatus.NEEDS_FULFILLMENT:
                        transaction.fulfillment_status = TransactionFulfillmentStatus.IN_PROGRESS

            else:
                error_string = f"For Etsy receipt id: {receipt.etsy_id} \nProdigi Outcome: {outcome}"
                send_mail('Prodigi Order Creation Error', error_string)
