from database.namespaces import ProdigiOrderSpace, ProdigiChargeSpace, ProdigiShipmentSpace, ProdigiShipmentItemSpace, \
    ProdigiFulfillmentLocationSpace, ProdigiRecipientSpace, ProdigiItemSpace, ProdigiCostSpace, ProdigiAssetSpace, \
    ProdigiPackingSlipSpace, ProdigiStatusSpace, ProdigiAuthorizationDetailsSpace, ProdigiIssueSpace, \
    ProdigiChargeItemSpace, ProdigiAddressSpace
from database.utils import make_engine
from database.etsy_tables import Address
from database.prodigi_tables import ProdigiOrder, ProdigiStatus, ProdigiCharge, ProdigiCost, ProdigiShipment, \
    ProdigiItem, ProdigiRecipient, ProdigiPackingSlip, ProdigiShipmentItem, ProdigiFulfillmentLocation, ProdigiAsset, \
    ProdigiIssue, ProdigiAuthorizationDetail, ProdigiChargeItem
from database.enums import Prodigi
from apis.prodigi import API as ProdigiAPI
from apis.etsy import API as EtsyAPI
from alerts.email import send_mail

from sqlalchemy.orm import Session


def main():
    # 1) Get all incomplete Prodigi Orders
    # 2) Call for updates
    # 3) Create the new database objects from call response
    # 4) Communicate any Etsy required updates
    # 5) Make any updates to Prodigi Order database record
    # 6) Alert to any issues

    prodigi_api = ProdigiAPI()
    etsy_api = EtsyAPI()
    with Session(make_engine()) as session:
        incomplete_orders = session.query(ProdigiOrder).join(ProdigiOrder.status).filter(
            ProdigiStatus.stage == Prodigi.StatusStage.IN_PROGRESS
        ).all()

        for prodigi_order in incomplete_orders:
            order_information = prodigi_api.get_order(prodigi_order.prodigi_id)
            order_information_space = ProdigiOrderSpace(order_information)

            # Update status
            status_space = ProdigiStatusSpace(order_information_space.status)
            issues = []
            for issue_dict in status_space.issues:
                issue_space = ProdigiIssueSpace(issue_dict)

                authorization_details_space = ProdigiAuthorizationDetailsSpace(issue_space.authorization_details)
                authorization_details = ProdigiAuthorizationDetail.create(authorization_details_space)

                issue = ProdigiIssue.get_existing(issue_space)
                if issue is None:
                    issue = ProdigiIssue.create(issue_space, authorization_details=authorization_details)
                    session.add(issue)
                    session.flush()
                else:
                    issue.update(issue_space, authorization_details=authorization_details)
                issues.append(issue)

            received_status = ProdigiStatus.create(status_space, issues=issues)

            # Update / create charges
            received_charges = []
            for charge_dict in order_information_space.charges:
                charge_space = ProdigiChargeSpace(charge_dict)

                total_cost_space = ProdigiCostSpace(charge_space.total_cost)
                total_cost = ProdigiCost.create(total_cost_space)

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
                    charge = ProdigiCharge.create(charge_space, order=prodigi_order, total_cost=total_cost,
                                                  items=charge_items)
                    session.add(charge)
                    session.flush()
                else:
                    charge.update(charge_space, order=prodigi_order, total_cost=total_cost, items=charge_items)
                received_charges.append(charge)

            # Update / create shipments
            received_shipments = []
            for shipment_dict in order_information_space.shipments:
                shipment_space = ProdigiShipmentSpace(shipment_dict)

                shipment_items = []
                for shipment_item_dict in shipment_space.items:
                    shipment_item_space = ProdigiShipmentItemSpace(shipment_item_dict)
                    shipment_item = ProdigiShipmentItem.get_existing(shipment_item_space.item_id)
                    if shipment_item is None:
                        shipment_item = ProdigiShipmentItem.create(shipment_item_space)
                        session.add(shipment_item)
                        session.flush()
                    shipment_items.append(shipment_item)

                fulfillment_location_space = ProdigiFulfillmentLocationSpace(shipment_space.fulfillment_location)
                fulfillment_location = ProdigiFulfillmentLocation.create(fulfillment_location_space)

                shipment = ProdigiShipment.get_existing(shipment_space.prodigi_id)
                if shipment is None:
                    shipment = ProdigiShipment.create(shipment_space, order=prodigi_order, items=shipment_items,
                                                      fulfillment_location=fulfillment_location)
                    session.add(shipment)
                    session.flush()

                    # Update the Etsy Receipt with shipment
                    note_to_buyer = 'Your order has been shipped. Thank you!'
                    etsy_api.create_receipt_shipment(receipt_id=prodigi_order.receipt.etsy_id, carrier=shipment.carrier,
                                                     tracking_code=shipment.tracking, note_to_buyer=note_to_buyer,
                                                     send_bcc=True)
                else:
                    shipment.update(shipment_space, items=shipment_items, fulfillment_location=fulfillment_location)
                received_shipments.append(shipment)

            # Update recipient
            recipient_space = ProdigiRecipientSpace(order_information_space.recipient)
            address_space = ProdigiAddressSpace(recipient_space.address)
            address = Address.create(address_space)
            received_recipient = ProdigiRecipient.create(recipient_space, addresses=[address])

            # Update / create items
            received_items = []
            for item_dict in order_information_space.items:
                item_space = ProdigiItemSpace(item_dict)

                recipient_cost_space = ProdigiCostSpace(item_space.recipient_cost)
                recipient_cost = ProdigiCost.create(recipient_cost_space)

                assets = []
                for asset_dict in item_space.assets:
                    asset_space = ProdigiAssetSpace(asset_dict)
                    asset = ProdigiAsset.get_existing(asset_space)
                    if asset is None:
                        asset = ProdigiAsset.create(asset_space)
                        session.add(asset)
                        session.flush()
                    assets.append(asset)

                item = ProdigiItem.get_existing(item_space)
                if item is None:
                    item = ProdigiItem.create(item_space, recipient_cost=recipient_cost, assets=assets)
                    session.add(item)
                    session.flush()
                else:
                    item.update(item_space, recipient_cost=recipient_cost, assets=assets)
                received_items.append(item)

            # Update / create packing slip
            packing_slip_space = ProdigiPackingSlipSpace(order_information_space.packing_slip)
            received_packing_slip = ProdigiPackingSlip.create(packing_slip_space)

            # Update order
            prodigi_order.update(order_information_space, status=received_status, charges=received_charges,
                                 shipments=received_shipments, recipient=received_recipient, items=received_items,
                                 packing_slip=received_packing_slip)

            status = prodigi_order.status

            # Send error report if there are any for each fulfillment stage
            email_alert = ''
            if status.download_assets == Prodigi.DetailStatus.ERROR:
                email_alert += 'Error downloading assets for one or more items\n'

            if status.print_ready_assets_prepared == Prodigi.DetailStatus.ERROR:
                email_alert += 'Error preparing print ready assets\n'

            if status.allocate_production_location == Prodigi.DetailStatus.ERROR:
                email_alert += 'Error allocating production location\n'

            if status.in_production == Prodigi.DetailStatus.ERROR:
                email_alert += 'Error in production\n'

            if status.shipping == Prodigi.DetailStatus.ERROR:
                email_alert += 'Error with shipping\n'

            if email_alert != '':
                email_alert += 'Issues:\n'
                for issue in status.issues:
                    email_alert += issue.alert_string()
                send_mail(f'Order #{prodigi_order.prodigi_id} Error Report', email_alert)
