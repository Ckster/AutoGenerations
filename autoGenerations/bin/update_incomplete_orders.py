from database.namespaces import ProdigiOrderSpace, ProdigiChargeSpace, ProdigiShipmentSpace, ProdigiShipmentItemSpace, \
    ProdigiFulfillmentLocationSpace, ProdigiRecipientSpace, ProdigiItemSpace, ProdigiCostSpace, ProdigiAssetSpace, \
    ProdigiPackingSlipSpace, ProdigiStatusSpace, ProdigiAuthorizationDetailsSpace, ProdigiIssueSpace, \
    ProdigiChargeItemSpace, ProdigiAddressSpace
from database.utils import make_engine
from database.etsy_tables import Address, EtsyReceipt
from database.prodigi_tables import ProdigiCharge, ProdigiCost, ProdigiShipment, \
    ProdigiItem, ProdigiRecipient, ProdigiPackingSlip, ProdigiShipmentItem, ProdigiFulfillmentLocation, ProdigiAsset, \
    ProdigiIssue, ProdigiAuthorizationDetails, ProdigiChargeItem
from database.enums import Prodigi, OrderStatus, Etsy
from apis.prodigi import API as ProdigiAPI
from apis.etsy import API as EtsyAPI
from alerts.email import send_mail

from sqlalchemy.orm import Session


def main():
    """


    Note on overwriting... there are some objects that come from Prodigi without an ID. For example, each issue in the
    list of status issues returned from the order info endpoint come without an ID. We could compare each of the new
    issue's attributes to those of each existings' attributes to see if it is really new or not. We would also have to
    compare the attributres of its relationships. Also, this would not solve the case in which an item is removed /
    deleted on Prodigi's end and we now need to remove the record in the database. So, for the sake of keeping things
    simple, un-ID'd object will be overwritten on each update, even if the data is exactly is the same, because it is
    too much of a pain to check if it's the exact same or not.

    :return:
    """
    # 1) Get all incomplete Prodigi Orders
    # 2) Call for updates
    # 3) Create the new database objects from call response
    # 4) Communicate any Etsy required updates
    # 5) Make any updates to Prodigi Order database record
    # 6) Alert to any issues

    prodigi_api = ProdigiAPI()
    etsy_api = EtsyAPI()
    with Session(make_engine()) as session:
        incomplete_fulfilled_receipts = session.query(EtsyReceipt).filter(
            EtsyReceipt.order_status == Etsy.OrderStatus.INCOMPLETE
        ).filter(
            EtsyReceipt.needs_fulfillment == False  # TODO: Fix this
        ).all()

        for etsy_receipt in incomplete_fulfilled_receipts:

            for prodigi_order in etsy_receipt.prodigi_orders:
                order_information = prodigi_api.get_order(prodigi_order.prodigi_id)
                order_information_space = ProdigiOrderSpace(order_information)

                # Update the status attributes
                issues = []
                for new_issue_dict in status_space.issues:
                    new_issue_space = ProdigiIssueSpace(new_issue_dict)
                    authorization_details_space = ProdigiAuthorizationDetailsSpace(new_issue_space.authorization_details)
                    payment_details_space = ProdigiCostSpace(authorization_details_space.payment_details)

                    payment_details = ProdigiCost.create(payment_details_space)
                    authorization_details = ProdigiAuthorizationDetails.create(authorization_details_space,
                                                                               payment_details=payment_details)
                    issue = ProdigiIssue.create(new_issue_space, authorization_details=authorization_details)
                    issues.append(issue)

                status_space = ProdigiStatusSpace(order_information_space.status)
                prodigi_order.status.update(status_space, issues=issues, overwrite_list=True)

                # Update / create charges
                received_charges = []
                for charge_dict in order_information_space.charges:
                    charge_space = ProdigiChargeSpace(charge_dict)
                    total_cost_space = ProdigiCostSpace(charge_space.total_cost)

                    charge_items = []
                    for charge_item_dict in charge_space.items:
                        charge_item_space = ProdigiChargeItemSpace(charge_item_dict)
                        charge_item = ProdigiChargeItem.get_existing(session, charge_item_space.prodigi_id)
                        if charge_item is None:
                            charge_item = ProdigiChargeItem.create(charge_item_space)
                            session.add(charge_item)
                            session.flush()
                        else:
                            charge_item.update(charge_item_space)
                        charge_items.append(charge_item)

                    charge = ProdigiCharge.get_existing(session, charge_space.prodigi_id)
                    if charge is None:
                        total_cost = ProdigiCost.create(total_cost_space)
                        charge = ProdigiCharge.create(charge_space, total_cost=total_cost, charge_items=charge_items)
                        session.add(charge)
                        session.flush()
                    else:
                        charge.update(charge_space, charge_items=charge_items, overwrite_list=True)
                        total_cost = charge.total_cost
                        if total_cost is None:
                            total_cost = ProdigiCost.create(total_cost_space)
                            charge.total_cost = total_cost
                        else:
                            total_cost.update(total_cost_space)
                    received_charges.append(charge)

                # Update / create shipments
                received_shipments = []
                for shipment_dict in order_information_space.shipments:
                    shipment_space = ProdigiShipmentSpace(shipment_dict)

                    shipment_items = []
                    for shipment_item_dict in shipment_space.items:
                        shipment_item_space = ProdigiShipmentItemSpace(shipment_item_dict)
                        shipment_item = ProdigiShipmentItem.get_existing(session, shipment_item_space.item_id)
                        if shipment_item is None:
                            shipment_item = ProdigiShipmentItem.create(shipment_item_space)
                            session.add(shipment_item)
                            session.flush()
                        shipment_items.append(shipment_item)

                    fulfillment_location_space = ProdigiFulfillmentLocationSpace(shipment_space.fulfillment_location)

                    shipment = ProdigiShipment.get_existing(session, shipment_space.prodigi_id)
                    if shipment is None:
                        fulfillment_location = ProdigiFulfillmentLocation.create(fulfillment_location_space)
                        shipment = ProdigiShipment.create(shipment_space, shipment_items=shipment_items,
                                                          fulfillment_location=fulfillment_location)
                        session.add(shipment)
                        session.flush()

                        # Update the Etsy Receipt with shipment
                        note_to_buyer = 'Your order has been shipped. Thank you!'
                        etsy_api.create_receipt_shipment(receipt_id=prodigi_order.receipt.etsy_id,
                                                         carrier=shipment.carrier, tracking_code=shipment.tracking,
                                                         note_to_buyer=note_to_buyer, send_bcc=True)
                    else:
                        shipment.update(shipment_space, shipment_items=shipment_items, overwrite_list=True)
                        fulfillment_location = shipment.fulfillment_location
                        if fulfillment_location is None:
                            fulfillment_location = ProdigiFulfillmentLocation.create(fulfillment_location_space)
                            session.add(fulfillment_location)
                            session.flush()
                            shipment.fulfillment_location = fulfillment_location
                        else:
                            fulfillment_location.update(fulfillment_location_space)
                    received_shipments.append(shipment)

                # Update / create items
                received_items = []
                for item_dict in order_information_space.items:
                    item_space = ProdigiItemSpace(item_dict)

                    recipient_cost_space = ProdigiCostSpace(item_space.recipient_cost)

                    assets = []
                    for asset_dict in item_space.assets:
                        asset_space = ProdigiAssetSpace(asset_dict)
                        asset = ProdigiAsset.get_existing(session, asset_space)
                        if asset is None:
                            asset = ProdigiAsset.create(asset_space)
                            session.add(asset)
                            session.flush()
                        assets.append(asset)

                    item = ProdigiItem.get_existing(session, item_space.prodigi_id)
                    if item is None:
                        recipient_cost = ProdigiCost.create(recipient_cost_space)
                        item = ProdigiItem.create(item_space, recipient_cost=recipient_cost, assets=assets)
                        session.add(item)
                        session.flush()
                    else:
                        item.update(item_space, assets=assets, overwrite_list=True)
                        recipient_cost = item.recipient_cost
                        if recipient_cost is None:
                            recipient_cost = ProdigiCost.create(recipient_cost_space)
                            item.recipient_cost = recipient_cost
                        else:
                            recipient_cost.update(recipient_cost_space)
                    received_items.append(item)

                # Update / create packing slip
                packing_slip_space = ProdigiPackingSlipSpace(order_information_space.packing_slip)
                packing_slip = prodigi_order.packing_slip
                if packing_slip is None:
                    packing_slip = ProdigiPackingSlip.create(packing_slip_space)
                    prodigi_order.packing_slip = packing_slip
                else:
                    packing_slip.update(packing_slip_space)
                prodigi_order.packing_slip.update(packing_slip_space)

                # Update order
                prodigi_order.update(order_information_space, charges=received_charges, shipments=received_shipments,
                                     items=received_items)

                # Update recipient
                recipient = prodigi_order.recipient
                recipient_space = ProdigiRecipientSpace(order_information_space.recipient)

                address_space = ProdigiAddressSpace(recipient_space.address)
                address = Address.get_existing(session, address_space.zip, address_space.city, address_space.state,
                                               address_space.country, address_space.first_line,
                                               address_space.second_line)
                if address is None:
                    address = Address.create(address_space)
                    session.add(address)
                    session.flush()

                if recipient is None:
                    received_recipient = ProdigiRecipient.create(recipient_space, orders=[prodigi_order],
                                                                 addresses=[address])
                    session.add(received_recipient)
                else:
                    recipient.udpdate(recipient_space, orders=[prodigi_order], addresses=[address])

                status = prodigi_order.status

                # Send error report if there are new errors
                # TODO: Only send for new errors
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

                session.commit()

        if all(order.status.stage == Prodigi.StatusStage.COMPLETE for order in etsy_receipt.prodigi_orders):
            etsy_receipt.order_status = OrderStatus.COMPLETE

        # TODO: Send request to Etsy API updating the receipt to complete

        session.commit()
