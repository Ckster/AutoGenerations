import traceback
from typing import List
from database.namespaces import ProdigiOrderSpace, ProdigiChargeSpace, ProdigiShipmentSpace, ProdigiShipmentItemSpace, \
    ProdigiFulfillmentLocationSpace, ProdigiRecipientSpace, ProdigiItemSpace, ProdigiCostSpace, ProdigiAssetSpace, \
    ProdigiPackingSlipSpace, ProdigiStatusSpace, ProdigiAuthorizationDetailsSpace, ProdigiIssueSpace, \
    ProdigiChargeItemSpace, ProdigiAddressSpace, EtsyReceiptSpace
from database.utils import make_engine
from database.tables import ProdigiCharge, ProdigiCost, ProdigiShipment, \
    ProdigiItem, ProdigiRecipient, ProdigiPackingSlip, ProdigiShipmentItem, ProdigiFulfillmentLocation, ProdigiAsset, \
    ProdigiIssue, ProdigiAuthorizationDetails, ProdigiChargeItem, Address, EtsyReceipt
from database.enums import Prodigi, OrderStatus, Etsy
from apis.prodigi import API as ProdigiAPI
from apis.etsy import API as EtsyAPI
from alerts.email import send_mail

from sqlalchemy.orm import Session


def check_if_new_issue(input_issue: ProdigiIssue, existing_issues: List[ProdigiIssue]) -> bool:
    new_issue = True
    for issue in existing_issues:
        if issue.object_id == input_issue.object_id and issue.error_code == input_issue.error_code and \
                issue.description == input_issue.description:
            new_issue = False
            break
    return new_issue


def map_prodigi_carrier_to_etsy(prodigi_carrier: str) -> str:
    prodigi_carrier = prodigi_carrier.lower()
    if 'usps' in prodigi_carrier:
        return 'usps'
    if 'ups' in prodigi_carrier:
        return 'ups'
    if 'fedex' in prodigi_carrier:
        return 'fedex'
    if 'royal' in prodigi_carrier:
        return 'royal-mail'
    if 'dpd' in prodigi_carrier:
        return 'dpd'
    if 'direct' in prodigi_carrier and 'link' in prodigi_carrier:
        return 'postnord'
    if 'dhl' in prodigi_carrier:
        return 'dhl'

    return 'other'


def update_incomplete_orders():
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

    prodigi_api = ProdigiAPI(sandbox_mode=False)
    etsy_api = EtsyAPI()
    with Session(make_engine()) as session:
        incomplete_fulfilled_receipts = session.query(EtsyReceipt).filter(
            EtsyReceipt.order_status == OrderStatus.INCOMPLETE
        ).filter(
            EtsyReceipt.needs_fulfillment == False
        ).all()

        print(f'Updating {len(incomplete_fulfilled_receipts)} receipts')

        for etsy_receipt in incomplete_fulfilled_receipts:
            try:
                for prodigi_order in etsy_receipt.prodigi_orders:
                    order_information = prodigi_api.get_order(prodigi_order.prodigi_id)
                    order_information_space = ProdigiOrderSpace(order_information['order'])

                    # Update the status attributes
                    status_space = ProdigiStatusSpace(order_information_space.status)

                    issues = []
                    new_issues = []
                    for new_issue_dict in status_space.issues:
                        new_issue_space = ProdigiIssueSpace(new_issue_dict)

                        authorization_details = None
                        if new_issue_space.authorization_details is not None:
                            authorization_details_space = ProdigiAuthorizationDetailsSpace(
                                new_issue_space.authorization_details)
                            payment_details_space = ProdigiCostSpace(authorization_details_space.payment_details)
                            payment_details = ProdigiCost.create(payment_details_space)
                            authorization_details = ProdigiAuthorizationDetails.create(authorization_details_space,
                                                                                       payment_details=payment_details)

                        issue = ProdigiIssue.create(new_issue_space, authorization_details=authorization_details)
                        issues.append(issue)
                        if check_if_new_issue(issue, prodigi_order.status.issues):
                            new_issues.append(issue)

                    send_download_assets = prodigi_order.status.download_assets != Prodigi.DetailStatus.ERROR
                    send_print_ready = prodigi_order.status.print_ready_assets_prepared != Prodigi.DetailStatus.ERROR
                    send_allocate_production = prodigi_order.status.allocate_production_location != \
                                               Prodigi.DetailStatus.ERROR
                    send_in_production = prodigi_order.status.in_production != Prodigi.DetailStatus.ERROR
                    send_shipping = prodigi_order.status.shipping != Prodigi.DetailStatus.ERROR

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

                        else:
                            shipment.update(shipment_space, shipment_items=shipment_items)
                            fulfillment_location = shipment.fulfillment_location
                            if fulfillment_location is None:
                                fulfillment_location = ProdigiFulfillmentLocation.create(fulfillment_location_space)
                                session.add(fulfillment_location)
                                session.flush()
                                shipment.fulfillment_location = fulfillment_location
                            else:
                                fulfillment_location.update(fulfillment_location_space)
                        received_shipments.append(shipment)

                    # When the order stage is complete then all of the orders have been sent and we can post the
                    # shipping information
                    if status_space.stage == Prodigi.StatusStage.COMPLETE:

                        # Only post shipping if there are no shipments for the receipt. Don't want to duplicate shipping
                        # information
                        receipt_response = etsy_api.get_receipt(receipt_id=etsy_receipt.receipt_id)
                        receipt_space = EtsyReceiptSpace(receipt_response)
                        if not receipt_space.shipments:
                            # Update the Etsy Receipt with shipment
                            note_to_buyer = 'Your order has been shipped. Thank you!'
                            etsy_api.create_receipt_shipment(receipt_id=str(prodigi_order.etsy_receipt.receipt_id),
                                                             carrier=map_prodigi_carrier_to_etsy(shipment.carrier_name),
                                                             tracking_code=shipment.tracking_number,
                                                             note_to_buyer=note_to_buyer, send_bcc=True)
                            try:
                                shop_name = etsy_receipt.transactions[0].product.listings[0].shop_section.shop.shop_name
                                body = f'Your order has shipped. Thank you!'
                                if shipment.tracking_number is not None:
                                    body += f'\n The carrier shipping your order is {shipment.carrier_name} and the ' \
                                            f'tracking number is {shipment.tracking_number}'

                                if shipment.tracking_url is not None:
                                    body += f' You can use the following link to track your order: ' \
                                            f'{shipment.tracking_url}'

                                send_mail(f'Your Etsy Order from {shop_name} Has Shipped', body)
                            except Exception as e:
                                continue

                    # Update / create items
                    received_items = []
                    for item_dict in order_information_space.items:
                        item_space = ProdigiItemSpace(item_dict)

                        recipient_cost_space = ProdigiCostSpace(item_space.recipient_cost) if item_space.recipient_cost is \
                                                                                              not None else None

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
                            recipient_cost = ProdigiCost.create(recipient_cost_space) if recipient_cost_space is not None \
                                else None
                            item = ProdigiItem.create(item_space, recipient_cost=recipient_cost, assets=assets)
                            session.add(item)
                            session.flush()
                        else:
                            item.update(item_space, assets=assets, overwrite_list=True)
                            if recipient_cost_space is not None:
                                recipient_cost = item.recipient_cost
                                if recipient_cost is None:
                                    recipient_cost = ProdigiCost.create(recipient_cost_space)
                                    item.recipient_cost = recipient_cost
                                else:
                                    recipient_cost.update(recipient_cost_space)
                        received_items.append(item)

                    # Update / create packing slip
                    if order_information_space.packing_slip is not None:
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
                        recipient.update(orders=[prodigi_order], addresses=[address])

                    status = prodigi_order.status

                    # Send error report if there are new errors
                    email_alert = ''
                    if status.download_assets == Prodigi.DetailStatus.ERROR and send_download_assets:
                        email_alert += 'Error downloading assets for one or more items\n'

                    if status.print_ready_assets_prepared == Prodigi.DetailStatus.ERROR and send_print_ready:
                        email_alert += 'Error preparing print ready assets\n'

                    if status.allocate_production_location == Prodigi.DetailStatus.ERROR and send_allocate_production:
                        email_alert += 'Error allocating production location\n'

                    if status.in_production == Prodigi.DetailStatus.ERROR and send_in_production:
                        email_alert += 'Error in production\n'

                    if status.shipping == Prodigi.DetailStatus.ERROR and send_shipping:
                        email_alert += 'Error with shipping\n'

                    if new_issues:
                        email_alert += 'Issues:\n'
                        for issue in new_issues:
                            email_alert += issue.alert_string()

                    if email_alert != '':
                        send_mail(f'Order #{prodigi_order.prodigi_id} Error Report', email_alert)

                    session.commit()
            except Exception as e:
                send_mail(f'Update Incomplete Orders Error for receipt {etsy_receipt.receipt_id}',
                          str(traceback.format_exc()))


if __name__ == '__main__':
    try:
        update_incomplete_orders()
    except Exception as e:
        send_mail('Update Incomplete Orders Error', str(traceback.format_exc()))
