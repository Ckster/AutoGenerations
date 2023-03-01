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
from apis.prodigi import API as ProdigiAPI
from apis.etsy import API as EtsyAPI
from alerts.email import send_mail

from sqlalchemy.orm import Session


def main():
    # 1) Get all incomplete Prodigi Orders
    # 2) Call for updates
    # 3) Make any updates to Prodigi Order database record
    # 4) Alert to any issues
    # 5) Communicate any Etsy required updates
    # 6) When completed, change database status to completed

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
            # TODO: Update / create the issues
            status = prodigi_order.status
            status_space = ProdigiStatusSpace(order_information_space.status)
            status.update(status_space)

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

            # Update / create charges
            # TODO: Update total price?
            for charge_dict in order_information_space.charges:
                charge_space = ProdigiChargeSpace(charge_dict)
                charge = ProdigiCharge.get_existing(charge_space.prodigi_id)
                if charge is None:
                    charge = ProdigiCharge.create(charge_space, order=prodigi_order)
                    session.add(charge)
                    session.flush()
                else:
                    charge.update(charge_space)

            # Update / create shipments
            for shipment_dict in order_information_space.shipments:
                shipment_space = ProdigiShipmentSpace(shipment_dict)

                items = []
                for item_dict in shipment_space.items:
                    item_space = ProdigiItemSpace(item_dict)
                    item = ProdigiItem.get_existing(item_space.prodigi_id)
                    if item is None:
                        item = ProdigiItem.create(item_space)
                        session.add(item)
                        session.flush()
                    else:
                        item.update()
                    items.append(item)

                fulfillment_location_space = ProdigiFulfillmentLocationSpace(shipment_space.fulfillment_location)
                fulfillment_location = ProdigiFulfillmentLocation.create(fulfillment_location_space)

                shipment = ProdigiShipment.get_existing(shipment_space.prodigi_id)
                if shipment is None:
                    shipment = ProdigiShipment.create(shipment_space, order=prodigi_order, items=items,
                                                      fulfillment_location=fulfillment_location)
                    session.add(shipment)
                    session.flush()

                    # Update the Etsy Receipt with shipment
                    note_to_buyer = 'Thank you for your order! The following items will be included in this shipment:\n'
                    for item in items:
                        note_to_buyer += f'{item.merchant_reference}\n'
                    etsy_api.create_receipt_shipment(receipt_id=prodigi_order.receipt.etsy_id, carrier=shipment.carrier,
                                                     tracking_code=shipment.tracking, note_to_buyer=note_to_buyer,
                                                     send_bcc=True)
                else:
                    shipment.update(shipment_space, items=items, fulfillment_location=fulfillment_location)

            # Update recipient

            # Update / create items

            # Update / create packing slip

            # Update order

