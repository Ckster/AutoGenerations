# TODO: List IN_PROGRESS prodigi orders, etsy orders that need fulfillment, etsy orders that are not complete
# TODO: Be able to make API calls for in progress prodigi orders

import argparse
from database.utils import make_engine
from database.tables import ProdigiOrder, ProdigiStatus, ProdigiCharge, ProdigiCost, ProdigiShipment, \
    ProdigiItem, ProdigiRecipient, ProdigiPackingSlip, ProdigiShipmentItem, ProdigiFulfillmentLocation, ProdigiAsset, \
    ProdigiIssue, ProdigiAuthorizationDetails, ProdigiChargeItem, EtsyReceipt, Address
from database.enums import Prodigi, OrderStatus, Etsy

from sqlalchemy.orm import Session


def main(in_progress: bool, complete: bool, have_issues: bool):
    with Session(make_engine()) as session:
        prodigi_orders = session.query(ProdigiOrder)\

        if in_progress:
            prodigi_orders = prodigi_orders.filter(
                ProdigiOrder.status == Prodigi.OrderStatus.IN_PROGRESS
        )

        if complete:
            prodigi_orders = prodigi_orders.filter(
                ProdigiOrder.status == Prodigi.OrderStatus.COMPLETE
            )

        if have_issues:
            prodigi_orders = prodigi_orders.join(ProdigiStatus).filter(
                ProdigiStatus.issues != []
            )

        prodigi_orders = prodigi_orders.all()

        fmt = "{:10s} {:15s} {:15s} {:10s} {:10s} {:15s}"\

        header = fmt.format(
            'Prodigi ID', 'Created Time', 'Last Updated', 'Shipping Method', 'Status', 'Issues'
        )

        print(header)
        for order in prodigi_orders:
            issues = ''
            for issue in order.status.issues:
                issues += f'{issue.description} '
            print(fmt.format(
                order.prodigi_id, order.created_time, order.last_updated, order.shipping_method.value,
                order.status.value, issues
            ))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='Which action to take on the database: list', dest='command')

    # Add any main arguments here
    #parser.add_argument()
    list_parser = subparsers.add_parser("list_orders")
    list_parser.add_argument("--in_progress", action='store_true')
    list_parser.add_argument("--complete", action='store_true')
    list_parser.add_argument("--have_issues", action='store_true')
    args = parser.parse_args()

    if args.command:
        if args.command == 'list_orders':
            main(args.in_progress, args.complete, args.have_issues)


