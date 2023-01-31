from apis.etsy import API as EtsyAPI
from database.utils import make_engine
from database.tables import EtsyReceipt, Address, EtsyReceiptShipment, EtsyTransaction, EtsySeller, EtsyBuyer
from database.enums import Etsy as EtsyEnums
from database.unwrappers.receipts import AddressSpace, ReceiptSpace, BuyerSpace, SellerSpace, TransactionSpace,\
    EtsyReceiptShipmentSpace

from sqlalchemy.orm import Session

response = {'count': 1,
            'results': [{
                'receipt_id': 2780781914, 'receipt_type': 0, 'seller_user_id': 695701628,
                'seller_email': 'verleyeerick@gmail.com', 'buyer_user_id': 746422806,
                'buyer_email': 'erickverleye2@gmail.com', 'name': 'Erick',
                'first_line': '3303 Bluff St', 'second_line': 'Unit 211',
                'city': 'BOULDER', 'state': 'CO', 'zip': '80301',
                'status': 'Paid',
                'formatted_address': 'Erick\n3303 Bluff St\nUnit 211\nBOULDER, CO 80301\nUnited States',
                'country_iso': 'US', 'payment_method': 'cc', 'payment_email': '', 'message_from_payment': None,
                'message_from_seller': None, 'message_from_buyer': 'In Hoc Signo Vinces', 'is_shipped': False,
                'is_paid': True, 'create_timestamp': 1675134602, 'created_timestamp': 1675134602,
                'update_timestamp': 1675134622, 'updated_timestamp': 1675134622, 'is_gift': True,
                'gift_message': 'Congratulations', 'grandtotal': {'amount': 109, 'divisor': 100,
                                                                  'currency_code': 'USD'},
                'subtotal': {'amount': 100, 'divisor': 100, 'currency_code': 'USD'},
                'total_price': {'amount': 100, 'divisor': 100, 'currency_code': 'USD'},
                'total_shipping_cost': {'amount': 0, 'divisor': 100, 'currency_code': 'USD'},
                'total_tax_cost': {'amount': 9, 'divisor': 100, 'currency_code': 'USD'},
                'total_vat_cost': {'amount': 0, 'divisor': 100, 'currency_code': 'USD'},
                'discount_amt': {'amount': 0, 'divisor': 100, 'currency_code': 'USD'},
                'gift_wrap_price': {'amount': 0, 'divisor': 100, 'currency_code': 'USD'},
                'shipments': [], 'transactions': [{'transaction_id': 3414320431, 'title': 'TEST Do Not Buy',
                                                   'description': 'This is an API test product, please do not buy this '
                                                                  '- the order will not be fulfilled',
                                                   'seller_user_id': 695701628, 'buyer_user_id': 746422806,
                                                   'create_timestamp': 1675134602, 'created_timestamp': 1675134602,
                                                   'paid_timestamp': None, 'shipped_timestamp': None, 'quantity': 5,
                                                   'listing_image_id': 4626083805, 'receipt_id': 2780781914,
                                                   'is_digital': False, 'file_data': '', 'listing_id': 1406729485,
                                                   'sku': 'SKU101', 'product_id': 13311969728,
                                                   'transaction_type': 'listing',
                                                   'price': {'amount': 20, 'divisor': 100, 'currency_code': 'USD'},
                                                   'shipping_cost': {'amount': 0, 'divisor': 100,
                                                                     'currency_code': 'USD'}, 'variations': [],
                                                   'product_data': [], 'shipping_profile_id': 193275197951,
                                                   'min_processing_days': 5, 'max_processing_days': 7,
                                                   'shipping_method': None, 'shipping_upgrade': None,
                                                   'expected_ship_date': 1675912218, 'buyer_coupon': 0,
                                                   'shop_coupon': 0}], 'refunds': []

                    }
                ]
            }


def get_new_orders():
    etsy_api = EtsyAPI()

    # First get the last order that we have received that has not yet been completed
    with Session(make_engine()) as session:

        # Our database
        earliest_incomplete_order = session.query(EtsyReceipt).filter(
            EtsyReceipt.status != EtsyEnums.OrderStatus.COMPLETED
        ).order_by(
            EtsyReceipt.create_timestamp.asc()
        ).first()

        min_created = None if earliest_incomplete_order is None else earliest_incomplete_order.create_timestamp

        # Etsy API
        orders = etsy_api.get_receipts(min_created=min_created)

        print(f"Processing {orders['count']} new orders")

        for receipt in orders['results']:
            receipt_id = receipt['receipt_id']

            receipt_space = ReceiptSpace(receipt)
            address_space = AddressSpace(receipt)
            buyer_space = BuyerSpace(receipt)
            seller_space = SellerSpace(receipt)

            existing_receipt = session.query(EtsyReceipt).filter(EtsyReceipt.receipt_id == receipt_id).first()

            if existing_receipt is None:
                # This is a brand new receipt

                # Check if the address exists
                existing_address = session.query(Address).filter(
                    Address.zip == address_space.zip,
                    Address.city == address_space.city,
                    Address.state == address_space.state,
                    Address.country == address_space.country,
                    Address.first_line == address_space.first_line,
                    Address.second_line == address_space.second_line
                ).first()

                if existing_address is None:
                    address = Address(
                        zip=address_space.zip,
                        city=address_space.city,
                        state=address_space.state,
                        country=address_space.country,
                        first_line=address_space.first_line,
                        second_line=address_space.second_line
                    )
                    session.add(address)
                    session.flush()

                else:
                    address = existing_address

                # Check if the buyer exists
                existing_buyer = session.query(EtsyBuyer).filter(
                    EtsyBuyer.buyer_id == buyer_space.buyer_id
                ).first()

                if existing_buyer is None:
                    buyer = EtsyBuyer(
                        buyer_id=buyer_space.buyer_id,
                        name=buyer_space.name,
                        email=buyer_space.email
                    )
                    session.add(buyer)
                    session.flush()
                else:
                    buyer = existing_buyer

                # Check if the seller exists
                existing_seller = session.query(EtsySeller).filter(
                    EtsySeller.seller_id == seller_space.seller_id
                ).first()

                if existing_seller is None:
                    seller = EtsySeller(
                        seller_id=seller_space.seller_id,
                        name=seller_space.name,
                        email=seller_space.email
                    )
                    session.add(seller)
                    session.flush()
                else:
                    seller = existing_seller

                # Create new shipments
                # TODO: Make sure all of these shipments are related to the receipt... Or create the receipt first
                #  and then add them
                for shipment in receipt['shipments']:
                    receipt_shipment_space = EtsyReceiptShipmentSpace(shipment)

                    existing_receipt_shipment = session.query(EtsyReceiptShipment).filter(
                        EtsyReceiptShipment.receipt_shipping_id
                    ).first()

                    if existing_receipt_shipment is None:

                        # Establish the relationhsip to the receipt later on
                        receipt_shipment = EtsyReceiptShipment(
                            receipt_shipping_id=receipt_shipment_space.receipt_shipping_id,
                            shipment_notification_timestamp=receipt_shipment_space.shipment_notification_timestamp,
                            carrier_name=receipt_shipment_space.carrier_name,
                            tracking_code=receipt_shipment_space.tracking_code
                        )
                        session.add(receipt_shipment)
                        session.flush()

                    else:
                        receipt_shipment = existing_receipt_shipment

                # Create new transactions
                for transaction in receipt['transactions']:
                    transaction_space = TransactionSpace(transaction)

                    # Check for existing transaction
                    existing_transaction = session.query(EtsyTransaction).filter(
                        EtsyTransaction.transaction_id == transaction_space.transaction_id
                    ).first()

                    if existing_transaction is None:
                        # TODO: Make sure receipt, buyer, seller, product, and shipping_profile are already in the
                        #  database and then use their ids to make the transaction

                        transaction = EtsyTransaction(
                            transaction_id=transaction_space.transaction_id,
                            title=transaction_space.title,
                            description=transaction_space.description,
                            create_timestamp=transaction_space.create_timestamp,
                            paid_timestamp=transaction_space.paid_timestamp,
                            shipped_timestamp=transaction_space.shipped_timestamp,
                            quantity=transaction_space.quantity,
                            is_digital=transaction_space.is_digital,
                            file_data=transaction_space.file_date,
                            transaction_type=transaction_space.transaction_type,
                            shipping_cost=transaction_space.shipping_cost,
                            min_processing_days=transaction_space.min_processing_days,
                            max_processing_days=transaction_space.max_processing_days,
                            shipping_method=transaction_space.shipping_method,
                            shipping_upgrade=transaction_space.shipping_upgrade,
                            expected_ship_date=transaction_space.expected_ship_date,
                            buyer_coupon=transaction_space.buyer_coupon,
                            shop_coupon=transaction_space.shop_coupon,
                            # receipt_id=transaction_space.receipt_id,
                            # buyer_id=transaction_space.buyer_user_id,
                            # seller_id=transaction_space.seller_user_id,
                            # product_id=transaction_space.product_id,
                            # shipping_profile_id=transaction_space.shipping_profile_id
                        )

                        session.add(transaction)
                        session.flush()

                new_receipt = EtsyReceipt(
                    receipt_id=receipt_id,
                    receipt_type=receipt['receipt_type'],
                    status=receipt['status'],
                    payment_method=receipt['payment_method'],
                    message_from_seller=receipt['message_from_seller'],
                    message_from_buyer=receipt['message_from_buyer'],
                    message_from_payment=receipt['message_from_payment'],
                    is_paid=receipt['is_paid'],
                    is_shipped=receipt['is_shipped'],
                    create_timestamp=receipt['create_timestamp'],
                    created_timestamp=receipt['created_timestamp'],
                    update_timestamp=receipt['update_timestamp'],
                    updated_timestamp=receipt['updated_timestamp'],
                    is_gift=receipt['is_gift'],
                    gift_message=receipt['gift_message'],
                    grand_total=receipt['grandtotal']['amount'],
                    sub_total=receipt['subtotal']['amount'],
                    total_price=receipt['total_price']['amount'],
                    shipping_cost=receipt['total_shipping_cost']['amount'],
                    tax_cost=receipt['total_tax_cost']['amount'],
                    vat_cost=receipt['total_vat_cost']['amount'],
                    discount=receipt['discount_amt']['amount'],
                    gift_wrap_price=receipt['gift_wrap_price']['amount'],

                    address=address,


                )

                session.add(new_receipt)
                session.commit()

                pass
            else:
                # Look for updates
                pass

