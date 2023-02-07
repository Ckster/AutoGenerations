from typing import Dict, List


_SPECIAL_CHAR = '|'


def list_string_encode(list_of_strings: List[str]) -> str:
    """
    sqlite does not support array column types (postgres does), so in order to keep development db the same as
    production, arrays of strings will be stored as a single string with each element separated by a special character.

    From etsy array-of-strings docs: When creating or updating a listing, valid tag strings contain only letters,
    numbers, whitespace characters, -, ', ™, ©, and ®. (regex: /[^\p{L}\p{Nd}\p{Zs}\-'™©®]/u) Default value is null

    :return:
    """
    enc = ''
    for c in list_of_strings:
        enc += c + _SPECIAL_CHAR if not c == list_of_strings[-1] else ''
    return enc


def list_string_decode(enc: str) -> List[str]:
    return enc.split(_SPECIAL_CHAR)


class EtsyReceiptSpace:
    def __init__(self, receipt: Dict):
        self.receipt_id = receipt['receipt_id']
        self.receipt_type = receipt['receipt_type']
        self.buyer_id = receipt['buyer_user_id']
        self.buyer_email = receipt['buyer_email']
        self.seller_id = receipt['seller_user_id']
        self.seller_email = receipt['seller_email']
        self.status = receipt['status']
        self.payment_method = receipt['payment_method']
        self.message_from_seller = receipt['message_from_seller']
        self.message_from_buyer = receipt['message_from_buyer']
        self.message_from_payment = receipt['message_from_payment']
        self.is_paid = receipt['is_paid']
        self.is_shipped = receipt['is_shipped']
        self.create_timestamp = receipt['create_timestamp']
        self.created_timestamp = receipt['created_timestamp']
        self.update_timestamp = receipt['update_timestamp']
        self.updated_timestamp = receipt['updated_timestamp']
        self.is_gift = receipt['is_gift']
        self.gift_message = receipt['gift_message']
        self.grand_total = receipt['grandtotal']['amount']
        self.sub_total = receipt['subtotal']['amount']
        self.total_price = receipt['total_price']['amount']
        self.shipping_cost = receipt['total_shipping_cost']['amount']
        self.tax_cost = receipt['total_tax_cost']['amount']
        self.vat_cost = receipt['total_vat_cost']['amount']
        self.discount = receipt['discount_amt']['amount']
        self.gift_wrap_price = receipt['gift_wrap_price']['amount']


class EtsyBuyerSpace:
    def __init__(self, receipt: Dict):
        self.buyer_id = receipt['buyer_user_id']
        self.email = receipt['buyer_email']


class EtsySellerSpace:
    def __init__(self, receipt: Dict):
        self.seller_id = receipt['seller_user_id']
        self.email = receipt['seller_email']


class AddressSpace:
    def __init__(self, receipt: Dict):
        self.zip = receipt['zip']
        self.city = receipt['city']
        self.state = receipt['state']
        self.country = receipt['country_iso']
        self.first_line = receipt['first_line']
        self.second_line = receipt['second_line']
        self.formatted_address = receipt['formatted_address']


class EtsyTransactionSpace:
    def __init__(self, transaction: Dict):
        self.transaction_id = transaction['transaction_id']
        self.title = transaction['title']
        self.description = transaction['description']
        self.seller_user_id = transaction['seller_user_id']
        self.buyer_user_id = transaction['buyer_user_id']
        self.create_timestamp = transaction['create_timestamp']
        self.created_timestamp = transaction['created_timestamp']
        self.paid_timestamp = transaction['paid_timestamp']
        self.shipped_timestamp = transaction['shipped_timestamp']
        self.quantity = transaction['quantity']
        self.listing_image_id = transaction['listing_image_id']
        self.receipt_id = transaction['receipt_id']
        self.is_digital = transaction['is_digital']
        self.file_date = transaction['file_data']
        self.listing_id = transaction['listing_id']
        self.sku = transaction['sku']
        self.product_id = transaction['product_id']
        self.transaction_type = transaction['transaction_type']
        self.price = transaction['price']['amount']
        self.shipping_cost = transaction['shipping_cost']['amount']
        self.variations = transaction['variations']
        self.product_property_data = transaction['product_data']
        self.shipping_profile_id = transaction['shipping_profile_id']
        self.min_processing_days = transaction['min_processing_days']
        self.max_processing_days = transaction['max_processing_days']
        self.shipping_method = transaction['shipping_method']
        self.shipping_upgrade = transaction['shipping_upgrade']
        self.expected_ship_date = transaction['expected_ship_date']
        self.buyer_coupon = transaction['buyer_coupon']
        self.shop_coupon = transaction['shop_coupon']


class EtsyReceiptShipmentSpace:
    def __init__(self, receipt_shipment: Dict):
        self.receipt_shipping_id = receipt_shipment['receipt_shipping_id']
        self.shipment_notification_timestamp = receipt_shipment['shipment_notification_timestamp']
        self.carrier_name = receipt_shipment['carrier_name']
        self.tracking_code = receipt_shipment['tracking_code']


class EtsyProductSpace:
    def __init__(self, product: Dict):
        self.product_id = product['product_id']
        self.sku = product['sku']
        self.price = product['price']


class EtsyProductPropertySpace:
    def __init__(self, product_data: Dict):
        self.property_id = product_data['property_id']
        self.property_name = product_data['property_name']
        self.scale_id = product_data['scale_id']
        self.scale_name = product_data['scale_name']
        self.value_ids = product_data['value_ids']
        self.values = product_data['values']


class EtsyShippingProfileSpace:
    def __init__(self, shipping_profile_data: Dict):
        self.shipping_profile_id = shipping_profile_data['shipping_profile_id']
        self.title = shipping_profile_data['title']
        self.user_id = shipping_profile_data['user_id']
        self.min_processing_days = shipping_profile_data['min_processing_days']
        self.max_processing_days = shipping_profile_data['max_processing_days']
        self.processing_days_display_label = shipping_profile_data['processing_days_display_label']
        self.origin_country_iso = shipping_profile_data['origin_country_iso']
        self.is_deleted = shipping_profile_data['is_deleted']
        self.shipping_profile_destinations = shipping_profile_data['shipping_profile_destinations']
        self.shipping_profile_upgrades = shipping_profile_data['shipping_profile_upgrades']
        self.origin_postal_code = shipping_profile_data['origin_postal_code']
        self.profile_type = shipping_profile_data['profile_type']
        self.domestic_handling_fee = shipping_profile_data['domestic_handling_fee']
        self.international_handling_fee = shipping_profile_data['international_handling_fee']


class EtsyShippingProfileDestinationSpace:
    def __init__(self, shipping_profile_destination_data: Dict):
        self.shipping_profile_destination_id = shipping_profile_destination_data['shipping_profile_destination_id']
        self.shipping_profile_id = shipping_profile_destination_data['shipping_profile_id']
        self.origin_country_iso = shipping_profile_destination_data['origin_country_iso']
        self.destination_country_iso = shipping_profile_destination_data['destination_country_iso']
        self.destination_region = shipping_profile_destination_data['destination_region']
        self.primary_cost = shipping_profile_destination_data['primary_cost']['amount']
        self.secondary_cost = shipping_profile_destination_data['secondary_cost']['amount']
        self.shipping_carrier_id = shipping_profile_destination_data['shipping_carrier_id']
        self.mail_class = shipping_profile_destination_data['mail_class']
        self.min_delivery_days = shipping_profile_destination_data['min_delivery_days']
        self.max_delivery_days = shipping_profile_destination_data['max_delivery_days']


class EtsyShippingProfileUpgradeSpace:
    def __init__(self, shipping_profile_upgrade_data: Dict):
        self.shipping_profile_id = shipping_profile_upgrade_data['shipping_profile_id']
        self.upgrade_id = shipping_profile_upgrade_data['upgrade_id']
        self.upgrade_name = shipping_profile_upgrade_data['upgrade_name']
        self.type = shipping_profile_upgrade_data['type']
        self.rank = shipping_profile_upgrade_data['rank']
        self.language = shipping_profile_upgrade_data['language']
        self.price = shipping_profile_upgrade_data['price']['amount']
        self.secondary_price = shipping_profile_upgrade_data['secondary_price']['amount']
        self.shipping_carrier_id = shipping_profile_upgrade_data['shipping_carrier_id']
        self.mail_class = shipping_profile_upgrade_data['mail_class']
        self.min_delivery_days = shipping_profile_upgrade_data['min_delivery_days']
        self.max_delivery_days = shipping_profile_upgrade_data['max_delivery_days']


class EtsyListingSpace:
    def __init__(self, listing_data: Dict):
        self.listing_id = listing_data['listing_id']
        self.user_id = listing_data['user_id']
        self.shop_id = listing_data['shop_id']
        self.title = listing_data['title']
        self.description = listing_data['description']
        self.state = listing_data['state']
        self.creation_timestamp = listing_data['creation_timestamp']
        self.created_timestamp = listing_data['created_timestamp']
        self.ending_timestamp = listing_data['ending_timestamp']
        self.original_creation_timestamp = listing_data['original_creation_timestamp']
        self.last_modified_timestamp = listing_data['last_modified_timestamp']
        self.updated_timestamp = listing_data['updated_timestamp']
        self.state_timestamp = listing_data['state_timestamp']
        self.quantity = listing_data['quantity']
        self.shop_section_id = listing_data['shop_section_id']
        self.featured_rank = listing_data['featured_rank']
        self.url = listing_data['url']
        self.num_favorers = listing_data['num_favorers']
        self.non_taxable = listing_data['non_taxable']
        self.is_taxable = listing_data['is_taxable']
        self.is_customizable = listing_data['is_customizable']
        self.is_personalizable = listing_data['is_personalizable']
        self.personalization_is_required = listing_data['personalization_is_required']
        self.personalization_char_count_max = listing_data['personalization_char_count_max']
        self.personalization_instructions = listing_data['personalization_instructions']
        self.listing_type = listing_data['listing_type']
        self.tags = listing_data['tags']
        self.materials = listing_data['materials']
        self.shipping_profile_id = listing_data['shipping_profile_id']
        self.return_policy_id = listing_data['return_policy_id']
        self.processing_min = listing_data['processing_min']
        self.processing_max = listing_data['processing_max']
        self.who_made = listing_data['who_made']
        self.when_made = listing_data['when_made']
        self.is_supply = listing_data['is_supply']
        self.item_weight = listing_data['item_weight']
        self.item_weight_unit = listing_data['item_weight_unit']
        self.item_length = listing_data['item_length']
        self.item_height = listing_data['item_height']
        self.item_dimensions_unit = listing_data['item_dimensions_unit']
        self.is_private = listing_data['is_private']
        self.style = listing_data['style']
        self.file_data = listing_data['file_data']
        self.has_variations = listing_data['has_variations']
        self.should_auto_renew = listing_data['should_auto_renew']
        self.language = listing_data['language']
        self.price = listing_data['price']['amount']
        self.taxonomy_id = listing_data['taxonomy_id']
        self.shipping_profile = listing_data['shipping_profile']
        self.user = listing_data['user']
        self.shop = listing_data['shop']
        self.images = listing_data['images']
        self.videos = listing_data['videos']
        self.inventory = listing_data['inventory']
        self.production_partners = listing_data['production_partners']
        self.skus = listing_data['skus']
        self.translations = listing_data['translations']
        self.views = listing_data['views']


class EtsyReturnPolicySpace:
    def __init__(self, return_policy_data: Dict):
        self.return_policy_id = return_policy_data['return_policy_id']
        self.shop_id = return_policy_data['shop_id']
        self.accepts_return = return_policy_data['accepts_return']
        self.accepts_exchanges = return_policy_data['accepts_exchanges']
        self.return_deadline = return_policy_data['return_deadline']


class EtsyShopSectionSpace:
    def __init__(self, shop_section_data: Dict):
        self.shop_section_id = shop_section_data['shop_section_id']
        self.title = shop_section_data['title']
        self.rank = shop_section_data['rank']
        self.user_id = shop_section_data['user_id']
        self.active_listing_count = shop_section_data['active_listing_count']


class EtsyProductionPartnerSpace:
    def __init__(self, production_partner: Dict):
        self.production_partner_id = production_partner['production_partner_id']
        self.partner_name = production_partner['partner_name']
        self.location = production_partner['location']


class EtsyShopSpace:
    def __init__(self, etsy_shop_data: Dict):
        self.shop_id = etsy_shop_data['shop_id']
        self.user_id = etsy_shop_data['user_id']
        self.shop_name = etsy_shop_data['shop_name']
        self.create_date = etsy_shop_data['create_date']
        self.created_date = etsy_shop_data['created_date']
        self.title = etsy_shop_data['title']
        self.announcement = etsy_shop_data['announcement']
        self.currency_code = etsy_shop_data['currency_code']
        self.is_vacation = etsy_shop_data['is_vacation']
        self.vacation_message = etsy_shop_data['vacation_message']
        self.sale_message = etsy_shop_data['sale_message']
        self.digital_sale_message = etsy_shop_data['digital_sale_message']
        self.update_date = etsy_shop_data['update_date']
        self.updated_timestamp = etsy_shop_data['updated_timestamp']
        self.listing_active_count = etsy_shop_data['listing_active_count']
        self.digital_listing_count = etsy_shop_data['digital_listing_count']
        self.login_name = etsy_shop_data['login_name']
        self.accepts_custom_requests = etsy_shop_data['accepts_custom_requests']
        self.policy_welcome = etsy_shop_data['policy_welcome']
        self.policy_payment = etsy_shop_data['policy_payment']
        self.policy_shipping = etsy_shop_data['policy_shipping']
        self.policy_refunds = etsy_shop_data['policy_refunds']
        self.policy_additional = etsy_shop_data['policy_additional']
        self.policy_seller_info = etsy_shop_data['policy_seller_info']
        self.policy_update_date = etsy_shop_data['policy_update_date']
        self.policy_has_private_receipt_info = etsy_shop_data['policy_has_private_receipt_info']
        self.has_unstructured_policies = etsy_shop_data['has_unstructured_policies']
        self.policy_privacy = etsy_shop_data['policy_privacy']
        self.vacation_autoreply = etsy_shop_data['vacation_autoreply']
        self.url = etsy_shop_data['url']
        self.image_url_760x100 = etsy_shop_data['image_url_760x100']
        self.num_favorers = etsy_shop_data['num_favorers']
        self.languages = etsy_shop_data['languages']
        self.icon_url_fullxfull = etsy_shop_data['icon_url_fullxfull']
        self.is_using_structured_policies = etsy_shop_data['is_using_structured_policies']
        self.has_onboarded_structured_policies = etsy_shop_data['has_onboarded_structured_policies']
        self.include_dispute_form_link = etsy_shop_data['include_dispute_form_link']
        self.is_etsy_payments_onboarded = etsy_shop_data['is_etsy_payments_onboarded']
        self.is_calculated_eligible = etsy_shop_data['is_calculated_eligible']
        self.is_opted_into_buyer_promise = etsy_shop_data['is_opted_into_buyer_promise']
        self.is_shop_us_based = etsy_shop_data['is_shop_us_based']
        self.transaction_sold_account = etsy_shop_data['transaction_sold_account']
        self.shipping_from_country_iso = etsy_shop_data['shipping_from_country_iso']
        self.shop_location_country_iso = etsy_shop_data['shop_location_country_iso']
        self.review_count = etsy_shop_data['review_count']
        self.review_average = etsy_shop_data['review_average']


class EtsyOfferingSpace:
    def __init__(self, offering_data: Dict):
        self.offering_id = offering_data['offering_id']
        self.quantity = offering_data['quantity']
        self.is_enabled = offering_data['is_enabled']
        self.is_deleted = offering_data['is_deleted']
        self.price = offering_data['price']['amount']
