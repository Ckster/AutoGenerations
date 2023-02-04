from apis.etsy import API as EtsyAPI
from database.utils import make_engine
from database.tables import EtsyReceipt, Address, EtsyReceiptShipment, EtsyTransaction, EtsySeller, EtsyBuyer,\
    EtsyProduct, EtsyProductProperty
from database.enums import Etsy as EtsyEnums

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

listing = {'listing_id': 1406729485, 'user_id': 695701628, 'shop_id': 40548296, 'title': 'TEST Do Not Buy',
           'description': 'This is an API test product, please do not buy this - the order will not be fulfilled',
           'state': 'active', 'creation_timestamp': 1675134605, 'created_timestamp': 1675134605,
           'ending_timestamp': 1685499005, 'original_creation_timestamp': 1675134217,
           'last_modified_timestamp': 1675137484, 'updated_timestamp': 1675137484, 'state_timestamp': 1675134580,
           'quantity': 15, 'shop_section_id': None, 'featured_rank': -1,
           'url': 'https://www.etsy.com/listing/1406729485/test-do-not-buy',
           'num_favorers': 0, 'non_taxable': False, 'is_taxable': True, 'is_customizable': False,
           'is_personalizable': False, 'personalization_is_required': False, 'personalization_char_count_max': None,
           'personalization_instructions': None, 'listing_type': 'physical', 'tags': [], 'materials': [],
           'shipping_profile_id': 192161103378, 'return_policy_id': 1115979002120, 'processing_min': 5,
           'processing_max': 7, 'who_made': 'i_did', 'when_made': 'made_to_order', 'is_supply': False,
           'item_weight': None, 'item_weight_unit': None, 'item_length': None, 'item_width': None, 'item_height': None,
           'item_dimensions_unit': None, 'is_private': False, 'style': [], 'file_data': '', 'has_variations': False,
           'should_auto_renew': True, 'language': 'en-US',
           'price': {'amount': 20, 'divisor': 100, 'currency_code': 'USD'}, 'taxonomy_id': 2078,
           'production_partners': [], 'skus': ['SKU101'], 'views': 2, 'shipping_profile': None, 'shop': None,
           'images': None, 'videos': None, 'user': None, 'translations': None, 'inventory': None}

product = {'product_id': 13311969728, 'sku': 'SKU101', 'is_deleted': False,
           'offerings': [{'offering_id': 13273503598, 'quantity': 15, 'is_enabled': True, 'is_deleted': False,
                          'price': {'amount': 20, 'divisor': 100, 'currency_code': 'USD'}}], 'property_values': []}

# TODO: Need to find a way to map listing to products... not sure why inventory field returns None for current listing


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

        orders = response

        for receipt in orders['results']:
            receipt_space = EtsyReceipt.create_namespace(receipt)

            # Check if the address exists
            existing_address = Address.get_existing(session, receipt)
            if existing_address is None:
                address = Address.create(receipt)
                session.add(address)
                session.flush()
            else:
                # Nothing to update, if anything changes it becomes a different address
                address = existing_address

            # Check if the buyer exists
            existing_buyer = EtsyBuyer.get_existing(session, receipt_space.buyer_id)
            if existing_buyer is None:
                buyer = EtsyBuyer.create(receipt)
                session.add(buyer)
                session.flush()
            else:
                existing_buyer.update(receipt)
                buyer = existing_buyer

            # Check if the seller exists
            existing_seller = EtsySeller.get_existing(session, receipt_space.seller_id)
            if existing_seller is None:
                seller = EtsySeller.create(receipt)
                session.add(seller)
                session.flush()
            else:
                existing_seller.update(receipt)
                seller = existing_seller

            # Create new shipments
            receipt_shipments = []
            for shipment in receipt['shipments']:
                existing_receipt_shipment = EtsyReceiptShipment.get_existing(session, shipment)
                if existing_receipt_shipment is None:
                    receipt_shipment = EtsyReceiptShipment.create(shipment)
                    session.add(receipt_shipment)
                    session.flush()
                else:
                    existing_receipt_shipment.update(shipment)
                    receipt_shipment = existing_receipt_shipment
                receipt_shipments.append(receipt_shipment)

            # Create new transactions
            transactions = []
            for transaction in receipt['transactions']:
                transaction_space = EtsyTransaction.create_namespace(transaction)

                # TODO: Do something with the listing id, for example we need to 1.) Keep an updated list of our stores
                #  listings 2) Make sure to increase the quantity available when stock gets low (etsy only lets you
                #  stock an item to 999) 3) Here we will only add listings if they don't already exist, and update their
                #  status if we cannot find them.
                # Get list of existing / created product data
                product_properties = []
                for property_data in transaction_space.product_property_data:
                    existing_product_property = EtsyProductProperty.get_existing(session, property_data)
                    if existing_product_property is None:
                        product_property = EtsyProductProperty.create(property_data)
                        session.add(product_property)
                        session.flush()
                    else:
                        existing_product_property.update(property_data)
                        product_property = existing_product_property
                    product_properties.append(product_property)

                # The transaction gives us the product_id, but no other information about the product. Using the
                # listing id, we can call the get product endpoint and get the necessary info, which can be used to
                # update the existing product record or create a new one. If it cannot be found, update the status of
                # the record to NOT FOUND, or something
                existing_product = EtsyProduct.get_existing(session, transaction_space.product_id)
                if existing_product is None:

                    # Need to get product information from api endpoint

                    existing_product = EtsyProduct()
                    session.add(existing_product)
                    session.flush()
                    pass

                else:


                # Check for existing transaction
                existing_transaction = EtsyTransaction.get_existing(session, transaction)
                if existing_transaction is None:
                    # TODO: Relate the shipping profile with the transaction here by querying for it using the
                    #  shipping_profile_id
                    receipt_transaction = EtsyTransaction.create(transaction_space, buyer, seller, existing_product,
                                                             product_properties)
                    session.add(receipt_transaction)
                    session.flush()
                else:
                    # TODO: Update
                    receipt_transaction = existing_transaction
                transactions.append(receipt_transaction)

            # Check if receipt exists
            existing_receipt = EtsyReceipt.get_existing(session, receipt)
            if existing_receipt is None:
                new_receipt = EtsyReceipt.create(receipt, address, buyer, seller, transactions, receipt_shipments)
                session.add(new_receipt)
                session.flush()
            else:
                # TODO: Update
                pass

            session.commit()
