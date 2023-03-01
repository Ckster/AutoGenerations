from apis.etsy import API as EtsyAPI
from database.namespaces import EtsyReceiptShipmentSpace, EtsyProductPropertySpace, EtsyListingSpace, EtsyShopSpace, \
    EtsyShopSectionSpace, EtsyReturnPolicySpace, EtsyShippingProfileSpace, EtsyProductionPartnerSpace, \
    EtsyShippingProfileUpgradeSpace, EtsyShippingProfileDestinationSpace, EtsyProductSpace, EtsyOfferingSpace
from database.utils import make_engine
from database.etsy_tables import EtsyReceipt, Address, EtsyReceiptShipment, EtsyTransaction, EtsySeller, EtsyBuyer, \
    EtsyProduct, EtsyProductProperty, EtsyListing, EtsyShop, EtsyShopSection, EtsyReturnPolicy, EtsyShippingProfile, \
    EtsyProductionPartner, EtsyShippingProfileUpgrade, EtsyShippingProfileDestination, EtsyOffering
from database.enums import Etsy as EtsyEnums, OrderStatus, TransactionFulfillmentStatus

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

listing_example = {'listing_id': 1406729485, 'user_id': 695701628, 'shop_id': 40548296, 'title': 'TEST Do Not Buy',
                   'description': 'This is an API test product, please do not buy this - the order will not be fulfilled',
                   'state': 'active', 'creation_timestamp': 1675134605, 'created_timestamp': 1675134605,
                   'ending_timestamp': 1685499005, 'original_creation_timestamp': 1675134217,
                   'last_modified_timestamp': 1675137484, 'updated_timestamp': 1675137484,
                   'state_timestamp': 1675134580,
                   'quantity': 15, 'shop_section_id': None, 'featured_rank': -1,
                   'url': 'https://www.etsy.com/listing/1406729485/test-do-not-buy',
                   'num_favorers': 0, 'non_taxable': False, 'is_taxable': True, 'is_customizable': False,
                   'is_personalizable': False, 'personalization_is_required': False,
                   'personalization_char_count_max': None,
                   'personalization_instructions': None, 'listing_type': 'physical', 'tags': [], 'materials': [],
                   'shipping_profile_id': 192161103378, 'return_policy_id': 1115979002120, 'processing_min': 5,
                   'processing_max': 7, 'who_made': 'i_did', 'when_made': 'made_to_order', 'is_supply': False,
                   'item_weight': None, 'item_weight_unit': None, 'item_length': None, 'item_width': None,
                   'item_height': None,
                   'item_dimensions_unit': None, 'is_private': False, 'style': [], 'file_data': '',
                   'has_variations': False,
                   'should_auto_renew': True, 'language': 'en-US',
                   'price': {'amount': 20, 'divisor': 100, 'currency_code': 'USD'}, 'taxonomy_id': 2078,
                   'production_partners': [], 'skus': ['SKU101'], 'views': 2, 'shipping_profile': None, 'shop': None,
                   'images': None, 'videos': None, 'user': None, 'translations': None, 'inventory': None}

product_sample = {'product_id': 13311969728, 'sku': 'SKU101', 'is_deleted': False,
                  'offerings': [{'offering_id': 13273503598, 'quantity': 15, 'is_enabled': True, 'is_deleted': False,
                                 'price': {'amount': 20, 'divisor': 100, 'currency_code': 'USD'}}],
                  'property_values': []}


# TODO: Need to find a way to map listing to products... not sure why inventory field returns None for current listing
# TODO: Communicate any changes to existing Prodigi Orders - shipping changes, cancellations etc.


def get_new_orders():
    etsy_api = EtsyAPI()

    # First get the last order that we have received that has not yet been completed
    with Session(make_engine()) as session:

        # Our database
        earliest_incomplete_order = session.query(EtsyReceipt).filter(
            EtsyReceipt.order_status != OrderStatus.INCOMPLETE
        ).order_by(
            EtsyReceipt.create_timestamp.asc()
        ).first()

        min_created = None if earliest_incomplete_order is None else earliest_incomplete_order.create_timestamp

        # Etsy API
        orders = etsy_api.get_receipts(min_created=min_created)
        print(f"Processing {orders['count']} orders")
        for receipt in orders['results']:
            receipt_space = EtsyReceipt.create_namespace(receipt)

            # Check if the address exists
            address = Address.get_existing(session, receipt_space.zip, receipt_space.city, receipt_space.state,
                                           receipt_space.country, receipt_space.first_line, receipt_space.second_line)
            if address is None:
                address = Address.create(receipt)
                session.add(address)
                session.flush()
            else:
                # Nothing to update, if anything changes it becomes a different address
                address = address

            # Check if the buyer exists
            buyer = EtsyBuyer.get_existing(session, receipt_space.buyer_id)
            if buyer is None:
                buyer = EtsyBuyer.create(receipt, addresses=[address])
                session.add(buyer)
                session.flush()
            else:
                buyer.update(receipt, addresses=[address])
                session.flush()

            # Check if the seller exists
            seller = EtsySeller.get_existing(session, receipt_space.seller_id)
            if seller is None:
                seller = EtsySeller.create(receipt)
                session.add(seller)
                session.flush()
            else:
                seller.update(receipt)
                session.flush()

            # Create new shipments
            receipt_shipments = []
            for shipment in receipt['shipments']:
                shipment_space = EtsyReceiptShipmentSpace(shipment)
                receipt_shipment = EtsyReceiptShipment.get_existing(session, shipment_space.receipt_shipping_id)
                if receipt_shipment is None:
                    receipt_shipment = EtsyReceiptShipment.create(shipment)
                    session.add(receipt_shipment)
                    session.flush()
                else:
                    receipt_shipment.update(shipment)
                    session.flush()
                receipt_shipments.append(receipt_shipment)

            # Create new transactions
            transactions = []
            for transaction in receipt['transactions']:
                transaction_space = EtsyTransaction.create_namespace(transaction)

                # Get list of existing / created product properties
                product_properties = []
                for property_data in transaction_space.product_property_data:
                    property_data_space = EtsyProductPropertySpace(property_data)
                    product_property = EtsyProductProperty.get_existing(session, property_data_space.property_id,
                                                                        property_data_space.property_name)
                    if product_property is None:
                        product_property = EtsyProductProperty.create(property_data)
                        session.add(product_property)
                        session.flush()
                    else:
                        product_property.update(property_data)
                        session.flush()
                    product_properties.append(product_property)

                # Call endpoint to get more info about listing, then update / create a listing record
                listing_response = etsy_api.get_listing(transaction_space.listing_id)
                listing_space = EtsyListingSpace(listing_response)
                listing = EtsyListing.get_existing(session, listing_space.listing_id)
                if listing is None:
                    listing = EtsyListing.create(listing_space, seller=seller)
                    session.add(listing)
                    session.flush()
                else:
                    listing.update(listing_space, seller=seller)
                    session.flush()

                shop_response = etsy_api.get_shop(listing_space.shop_id)
                shop_space = EtsyShopSpace(shop_response)
                shop = EtsyShop.get_existing(session, shop_space.shop_id)
                if shop is None:
                    shop = EtsyShop.create(shop_space, seller=seller, listings=[listing])
                    session.add(shop)
                    session.flush()
                else:
                    shop.update(shop_space, seller=seller, listings=[listing], overwrite_list=True)
                    session.flush()

                # Listing should be part of a section but possible that it isn't
                if listing_space.shop_section_id is not None:
                    shop_section_response = etsy_api.get_shop_section(listing_space.shop_id,
                                                                      listing_space.shop_section_id)
                    shop_section_space = EtsyShopSectionSpace(shop_section_response)
                    shop_section = EtsyShopSection.get_existing(session, shop_section_space.shop_section_id)
                    if shop_section is None:
                        shop_section = EtsyShopSection.create(shop_section_space, seller=seller, listings=[listing],
                                                              shop=shop)
                        session.add(shop_section)
                        session.flush()
                    else:
                        shop_section.update(shop_section_space, seller=seller, listings=[listing], shop=shop)
                        session.flush()

                return_policy_response = etsy_api.get_return_policy(listing_space.shop_id,
                                                                    listing_space.return_policy_id)
                return_policy_space = EtsyReturnPolicySpace(return_policy_response)
                return_policy = EtsyReturnPolicy.get_existing(session, return_policy_space.return_policy_id)
                if return_policy is None:
                    return_policy = EtsyReturnPolicy.create(return_policy_space, shop=shop, listings=[listing])
                    session.add(return_policy)
                    session.flush()
                else:
                    return_policy.update(return_policy_space, listings=[listing], shop=shop)
                    session.flush()

                shipping_profile_response = etsy_api.get_shipping_profile(listing_space.shop_id,
                                                                          listing_space.shipping_profile_id)
                shipping_profile_space = EtsyShippingProfileSpace(shipping_profile_response)
                shipping_profile = EtsyShippingProfile.get_existing(session, shipping_profile_space.shipping_profile_id)
                if shipping_profile is None:
                    shipping_profile = EtsyShippingProfile.create(shipping_profile_space, seller=seller,
                                                                  listings=[listing])
                    session.add(shipping_profile)
                    session.flush()
                else:
                    shipping_profile.update(shipping_profile_response, listings=[listing], seller=seller)
                    session.flush()

                production_partners = []
                production_partners_response = etsy_api.get_production_partners(listing_space.shop_id)
                for production_partner in production_partners_response['results']:
                    production_partner_space = EtsyProductionPartnerSpace(production_partner)
                    production_partner = EtsyProductionPartner.get_existing(
                        session,
                        production_partner_space.production_partner_id)
                    if production_partner is None:
                        production_partner = EtsyProductionPartner.create(production_partner_space, listings=[listing])
                        session.add(production_partner)
                        session.flush()
                    else:
                        production_partner.update(production_partner, listings=[listing])
                        session.flush()
                    production_partners.append(production_partner)

                shipping_upgrades = []
                shipping_upgrades_repsonse = etsy_api.get_shop_shipping_profile_upgrades(
                    listing_space.shop_id, listing_space.shipping_profile_id)
                for shipping_upgrade in shipping_upgrades_repsonse['results']:
                    shipping_upgrade_space = EtsyShippingProfileUpgradeSpace(shipping_upgrade)
                    shipping_upgrade = EtsyShippingProfileUpgrade.get_existing(session,
                                                                               shipping_upgrade_space.upgrade_id)
                    if shipping_upgrade is None:
                        shipping_upgrade = EtsyShippingProfileUpgrade.create(shipping_upgrade_space,
                                                                             shipping_profile=shipping_profile)
                        session.add(shipping_upgrade)
                        session.flush()
                    else:
                        shipping_upgrade.update(shipping_upgrade_space, shipping_profile=shipping_profile)
                        session.flush()
                    shipping_upgrades.append(shipping_upgrade)

                shipping_destinations = []
                shipping_destinations_requests = etsy_api.get_shop_shipping_profile_destinations(
                    listing_space.shop_id, listing_space.shipping_profile_id)
                for shipping_destination in shipping_destinations_requests['results']:
                    shipping_destination_space = EtsyShippingProfileDestinationSpace(shipping_destination)
                    shipping_destination = EtsyShippingProfileDestination.get_existing(
                        session, shipping_destination_space.shipping_profile_destination_id)
                    if shipping_destination is None:
                        shipping_destination = EtsyShippingProfileDestination.create(shipping_destination_space,
                                                                                     shipping_profile=shipping_profile)
                        session.add(shipping_destination)
                        session.flush()
                    else:
                        shipping_destination.update(shipping_destination_space, shipping_profile=shipping_profile)
                        session.flush()
                    shipping_destinations.append(shipping_destination)

                # Call endpoint to get more info about the product, then update / create a product record
                product_response = etsy_api.get_listing_product(transaction_space.listing_id,
                                                                transaction_space.product_id)
                product_space = EtsyProductSpace(product_response)

                offerings = []
                for offering in product_space.offerings:
                    offering_space = EtsyOfferingSpace(offering)
                    offering = EtsyOffering.get_existing(session, offering_space.offering_id)
                    if offering is None:
                        offering = EtsyOffering.create(offering_space)
                        session.add(offering)
                        session.flush()
                    else:
                        offering.update(offering_space)
                        session.flush()
                    offerings.append(offering)

                product = EtsyProduct.get_existing(session, product_space.product_id)
                if product is None:
                    product = EtsyProduct.create(product_space, properties=product_properties, listings=[listing],
                                                 offerings=offerings)
                    session.add(product)
                    session.flush()
                else:
                    product.update(product_space, properties=product_properties, listings=[listing],
                                   offerings=offerings)
                    session.flush()

                # Check for existing transaction
                transaction = EtsyTransaction.get_existing(session, transaction_space.transaction_id)
                if transaction is None:
                    transaction = EtsyTransaction.create(
                        transaction_space, fulfillment_status=TransactionFulfillmentStatus.NEEDS_FULFILLMENT,
                        buyer=buyer, seller=seller, product=product, shipping_profile=shipping_profile,
                        product_properties=product_properties)
                    session.add(transaction)
                    session.flush()
                else:
                    transaction.update(transaction_space, buyer=buyer, seller=seller, product=product,
                                       shipping_profile=shipping_profile, product_properties=product_properties)
                    session.flush()
                transactions.append(transaction)

            # Check if receipt exists
            receipt_c = EtsyReceipt.get_existing(session, receipt_space.receipt_id)
            if receipt_c is None:
                receipt_c = EtsyReceipt.create(receipt_space, order_status=OrderStatus.INCOMPLETE,
                                               address=address, buyer=buyer, seller=seller,
                                               transactions=transactions, receipt_shipments=receipt_shipments)
                session.add(receipt_c)
                session.flush()
            else:
                receipt_c.update(receipt_space, order_status=OrderStatus.INCOMPLETE,
                                 address=address, buyer=buyer, seller=seller, transactions=transactions,
                                 receipt_shipments=receipt_shipments)
                session.flush()

        session.commit()
