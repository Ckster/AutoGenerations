from database.namespaces import ProdigiOrderSpace, ProdigiChargeSpace
from database.utils import make_engine
from database.etsy_tables import EtsyReceipt
from database.prodigi_tables import ProdigiOrder, ProdigiStatus, ProdigiCharge, ProdigiCost
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

                # TODO: Add shipments here

                # TODO: Add recipient here

                # TODO: Add items here

                # TODO: Add packing slip here

                # Order was successful so each transaction should be updated to IN_PROGRESS
                for transaction in receipt.transactions:
                    if transaction.fulfillment_status == TransactionFulfillmentStatus.NEEDS_FULFILLMENT:
                        transaction.fulfillment_status = TransactionFulfillmentStatus.IN_PROGRESS

            else:
                pass
                # TODO: Alert about an issue with the order
