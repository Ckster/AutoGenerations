from typing import Dict, List, Any
from database.enums import Etsy, Prodigi

from datetime import datetime

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


def prodigi_timestamp_to_datetime(timestamp: str) -> datetime:
    return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S")


def parse_value(input_dict: Dict[str, Any], *args):
    input_dict = input_dict
    value = None
    for arg in args:
        if input_dict is None:
            return None
        if arg in input_dict:
            value = input_dict[arg]
            input_dict = value
        else:
            value = None

    return value


class EtsyReceiptSpace:
    def __init__(self, receipt: Dict):
        self.receipt_id = parse_value(receipt, 'receipt_id')
        self.receipt_type = parse_value(receipt, 'receipt_type')
        self.buyer_id = parse_value(receipt, 'buyer_user_id')
        self.buyer_email = parse_value(receipt, 'buyer_email')
        self.first_line = parse_value(receipt, 'first_line')
        self.second_line = parse_value(receipt, 'second_line')
        self.city = parse_value(receipt, 'city')
        self.state = parse_value(receipt, 'state')
        self.zip = parse_value(receipt, 'zip')
        self.country = parse_value(receipt, 'country_iso')
        self.seller_id = parse_value(receipt, 'seller_user_id')
        self.seller_email = parse_value(receipt, 'seller_email')
        self.status = Etsy.OrderStatus(parse_value(receipt, 'status').lower())
        self.payment_method = parse_value(receipt, 'payment_method')
        self.message_from_seller = parse_value(receipt, 'message_from_seller')
        self.message_from_buyer = parse_value(receipt, 'message_from_buyer')
        self.message_from_payment = parse_value(receipt, 'message_from_payment')
        self.is_paid = parse_value(receipt, 'is_paid')
        self.is_shipped = parse_value(receipt, 'is_shipped')
        self.create_timestamp = datetime.utcfromtimestamp(parse_value(receipt, 'create_timestamp')) if \
            parse_value(receipt, 'create_timestamp') is not None else None
        self.created_timestamp = datetime.utcfromtimestamp(parse_value(receipt, 'created_timestamp')
                                                           ) if parse_value(receipt,
                                                                            'created_timestamp') is not None else None
        self.update_timestamp = datetime.utcfromtimestamp(parse_value(receipt, 'update_timestamp')
                                                          ) if parse_value(receipt,
                                                                           'update_timestamp') is not None else None
        self.updated_timestamp = datetime.utcfromtimestamp(parse_value(receipt, 'updated_timestamp')
                                                           ) if parse_value(receipt,
                                                                            'updated_timestamp') is not None else None
        self.is_gift = parse_value(receipt, 'is_gift')
        self.gift_message = parse_value(receipt, 'gift_message')
        self.grand_total = parse_value(receipt, 'grandtotal', 'amount')
        self.grand_total_divisor = parse_value(receipt, 'grandtotal', 'divisor')
        self.grand_total_currency_code = parse_value(receipt, 'grandtotal', 'currency_code')
        self.sub_total = parse_value(receipt, 'subtotal', 'amount')
        self.sub_total_divisor = parse_value(receipt, 'subtotal', 'divisor')
        self.sub_total_currency_code = parse_value(receipt, 'subtotal', 'currency_code')
        self.total_price = parse_value(receipt, 'total_price', 'amount')
        self.total_price_divisor = parse_value(receipt, 'total_price', 'divisor')
        self.total_price_currency_code = parse_value(receipt, 'total_price', 'currency_code')
        self.shipping_cost = parse_value(receipt, 'total_shipping_cost', 'amount')
        self.shipping_cost_divisor = parse_value(receipt, 'total_shipping_cost', 'divisor')
        self.shipping_cost_currency_code = parse_value(receipt, 'total_shipping_cost', 'currency_code')
        self.tax_cost = parse_value(receipt, 'total_tax_cost', 'amount')
        self.tax_cost_divisor = parse_value(receipt, 'total_tax_cost', 'divisor')
        self.tax_cost_currency_code = parse_value(receipt, 'total_tax_cost', 'currency_code')
        self.vat_cost = parse_value(receipt, 'total_vat_cost', 'amount')
        self.vat_cost_divisor = parse_value(receipt, 'total_vat_cost', 'divisor')
        self.vat_cost_currency_code = parse_value(receipt, 'total_vat_cost', 'currency_code')
        self.discount = parse_value(receipt, 'discount_amt', 'amount')
        self.discount_divisor = parse_value(receipt, 'discount_amt', 'divisor')
        self.discount_currency_code = parse_value(receipt, 'discount_amt', 'currency_code')
        self.gift_wrap_price = parse_value(receipt, 'gift_wrap_price', 'amount')
        self.gift_wrap_price_divisor = parse_value(receipt, 'gift_wrap_price', 'divisor')
        self.gift_wrap_price_currency_code = parse_value(receipt, 'gift_wrap_price', 'currency_code')
        self.refunds = parse_value(receipt, 'refunds')
        self.shipments = parse_value(receipt, 'shipments')
        self.transactions = parse_value(receipt, 'transactions')


class EtsyBuyerSpace:
    def __init__(self, buyer_data: Dict):
        self.buyer_id = parse_value(buyer_data, 'buyer_user_id')
        self.email = parse_value(buyer_data, 'buyer_email')
        self.name = parse_value(buyer_data, 'name')


class EtsySellerSpace:
    def __init__(self, seller_data: Dict):
        self.seller_id = parse_value(seller_data, 'seller_user_id')
        self.email = parse_value(seller_data, 'seller_email')


class AddressSpace:
    def __init__(self, address_data: Dict):
        self.zip = parse_value(address_data, 'zip')
        self.city = parse_value(address_data, 'city')
        self.state = parse_value(address_data, 'state')
        self.country = parse_value(address_data, 'country_iso')
        self.first_line = parse_value(address_data, 'first_line')
        self.second_line = parse_value(address_data, 'second_line')
        self.formatted_address = parse_value(address_data, 'formatted_address')


class EtsyTransactionSpace:
    def __init__(self, transaction: Dict):
        self.transaction_id = parse_value(transaction, 'transaction_id')
        self.title = parse_value(transaction, 'title')
        self.description = parse_value(transaction, 'description')
        self.seller_user_id = parse_value(transaction, 'seller_user_id')
        self.buyer_user_id = parse_value(transaction, 'buyer_user_id')
        self.create_timestamp = datetime.utcfromtimestamp(parse_value(transaction, 'create_timestamp')
                                                          ) if parse_value(transaction,
                                                                           'create_timestamp') is not None else None
        self.created_timestamp = datetime.utcfromtimestamp(parse_value(transaction, 'created_timestamp')
                                                           ) if parse_value(transaction,
                                                                            'created_timestamp') is not None else None
        self.paid_timestamp = datetime.utcfromtimestamp(parse_value(transaction, 'paid_timestamp')
                                                        ) if parse_value(transaction,
                                                                         'paid_timestamp') is not None else None
        self.shipped_timestamp = datetime.utcfromtimestamp(parse_value(transaction, 'shipped_timestamp')
                                                           ) if parse_value(transaction,
                                                                            'shipped_timestamp') is not None else None
        self.quantity = parse_value(transaction, 'quantity')
        self.listing_image_id = parse_value(transaction, 'listing_image_id')
        self.receipt_id = parse_value(transaction, 'receipt_id')
        self.is_digital = parse_value(transaction, 'is_digital')
        self.file_data = parse_value(transaction, 'file_data')
        self.listing_id = parse_value(transaction, 'listing_id')
        self.sku = parse_value(transaction, 'sku')
        self.product_id = parse_value(transaction, 'product_id')
        self.transaction_type = parse_value(transaction, 'transaction_type')
        self.price = parse_value(transaction, 'price', 'amount')
        self.price_divisor = parse_value(transaction, 'price', 'divisor')
        self.price_currency_code = parse_value(transaction, 'price', 'currency_code')
        self.shipping_cost = parse_value(transaction, 'shipping_cost', 'amount')
        self.shipping_cost_divisor = parse_value(transaction, 'shipping_cost', 'divisor')
        self.shipping_cost_currency_code = parse_value(transaction, 'shipping_cost', 'currency_code')
        self.variations = parse_value(transaction, 'variations')
        self.product_property_data = parse_value(transaction, 'product_data')
        self.shipping_profile_id = parse_value(transaction, 'shipping_profile_id')
        self.min_processing_days = parse_value(transaction, 'min_processing_days')
        self.max_processing_days = parse_value(transaction, 'max_processing_days')
        self.shipping_method = parse_value(transaction, 'shipping_method')
        self.shipping_upgrade = parse_value(transaction, 'shipping_upgrade')
        self.expected_ship_date = datetime.utcfromtimestamp(parse_value(transaction, 'expected_ship_date')
                                                            ) if parse_value(transaction, 'expected_ship_date') \
                                                                 is not None else None
        self.buyer_coupon = parse_value(transaction, 'buyer_coupon')
        self.shop_coupon = parse_value(transaction, 'shop_coupon')


class EtsyReceiptShipmentSpace:
    def __init__(self, receipt_shipment: Dict):
        self.receipt_shipping_id = parse_value(receipt_shipment, 'receipt_shipping_id')
        self.shipment_notification_timestamp = datetime.utcfromtimestamp(
            parse_value(receipt_shipment, 'shipment_notification_timestamp')
        ) if parse_value(receipt_shipment, 'shipment_notification_timestamp') is not None else None
        self.carrier_name = parse_value(receipt_shipment, 'carrier_name')
        self.tracking_code = parse_value(receipt_shipment, 'tracking_code')


class EtsyProductSpace:
    def __init__(self, product: Dict):
        self.product_id = parse_value(product, 'product_id')
        self.sku = parse_value(product, 'sku')
        self.is_deleted = parse_value(product, 'is_deleted')
        self.offerings = parse_value(product, 'offerings')


class EtsyProductPropertySpace:
    def __init__(self, product_data: Dict):
        self.property_id = parse_value(product_data, 'property_id')
        self.property_name = parse_value(product_data, 'property_name')
        self.scale_id = parse_value(product_data, 'scale_id')
        self.scale_name = parse_value(product_data, 'scale_name')
        self.value_ids = parse_value(product_data, 'value_ids')
        self.values = parse_value(product_data, 'values')


class EtsyShippingProfileSpace:
    def __init__(self, shipping_profile_data: Dict):
        self.shipping_profile_id = parse_value(shipping_profile_data, 'shipping_profile_id')
        self.title = parse_value(shipping_profile_data, 'title')
        self.user_id = parse_value(shipping_profile_data, 'user_id')
        self.min_processing_days = parse_value(shipping_profile_data, 'min_processing_days')
        self.max_processing_days = parse_value(shipping_profile_data, 'max_processing_days')
        self.processing_days_display_label = parse_value(shipping_profile_data, 'processing_days_display_label')
        self.origin_country_iso = parse_value(shipping_profile_data, 'origin_country_iso')
        self.is_deleted = parse_value(shipping_profile_data, 'is_deleted')
        self.shipping_profile_destinations = parse_value(shipping_profile_data, 'shipping_profile_destinations')
        self.shipping_profile_upgrades = parse_value(shipping_profile_data, 'shipping_profile_upgrades')
        self.origin_postal_code = parse_value(shipping_profile_data, 'origin_postal_code')
        self.profile_type = Etsy.ShippingProfileType(parse_value(shipping_profile_data, 'profile_type').lower()) if \
            parse_value(shipping_profile_data, 'profile_type') is not None else None
        self.domestic_handling_fee = parse_value(shipping_profile_data, 'domestic_handling_fee')
        self.international_handling_fee = parse_value(shipping_profile_data, 'international_handling_fee')


class EtsyShippingProfileDestinationSpace:
    def __init__(self, shipping_profile_destination_data: Dict):
        self.shipping_profile_destination_id = parse_value(shipping_profile_destination_data,
                                                           'shipping_profile_destination_id')
        self.shipping_profile_id = parse_value(shipping_profile_destination_data, 'shipping_profile_id')
        self.origin_country_iso = parse_value(shipping_profile_destination_data, 'origin_country_iso')
        self.destination_country_iso = parse_value(shipping_profile_destination_data, 'destination_country_iso')
        self.destination_region = parse_value(shipping_profile_destination_data, 'destination_region')
        self.primary_cost = parse_value(shipping_profile_destination_data, 'primary_cost', 'amount')
        self.primary_cost_divisor = parse_value(shipping_profile_destination_data, 'primary_cost', 'divisor')
        self.primary_cost_currency_code = parse_value(shipping_profile_destination_data, 'primary_cost', 'currency_code')
        self.secondary_cost = parse_value(shipping_profile_destination_data, 'secondary_cost', 'amount')
        self.secondary_cost_divisor = parse_value(shipping_profile_destination_data, 'secondary_cost', 'divisor')
        self.secondary_cost_currency_code = parse_value(shipping_profile_destination_data, 'secondary_cost',
                                                        'currency_code')
        self.shipping_carrier_id = parse_value(shipping_profile_destination_data, 'shipping_carrier_id')
        self.mail_class = parse_value(shipping_profile_destination_data, 'mail_class')
        self.min_delivery_days = parse_value(shipping_profile_destination_data, 'min_delivery_days')
        self.max_delivery_days = parse_value(shipping_profile_destination_data, 'max_delivery_days')


class EtsyShippingProfileUpgradeSpace:
    def __init__(self, shipping_profile_upgrade_data: Dict):
        self.shipping_profile_id = parse_value(shipping_profile_upgrade_data, 'shipping_profile_id')
        self.upgrade_id = parse_value(shipping_profile_upgrade_data, 'upgrade_id')
        self.upgrade_name = parse_value(shipping_profile_upgrade_data, 'upgrade_name')
        self.type = Etsy.ShippingUpgradeType(parse_value(shipping_profile_upgrade_data, 'type')) if \
            parse_value(shipping_profile_upgrade_data, 'type') is not None else None
        self.rank = parse_value(shipping_profile_upgrade_data, 'rank')
        self.language = parse_value(shipping_profile_upgrade_data, 'language')
        self.price = parse_value(shipping_profile_upgrade_data, 'price', 'amount')
        self.price_divisor = parse_value(shipping_profile_upgrade_data, 'price', 'divisor')
        self.price_currency_code = parse_value(shipping_profile_upgrade_data, 'price', 'currency_code')
        self.secondary_price = parse_value(shipping_profile_upgrade_data, 'secondary_price', 'amount')
        self.secondary_price_divisor = parse_value(shipping_profile_upgrade_data, 'secondary_price', 'divisor')
        self.secondary_price_currency_code = parse_value(shipping_profile_upgrade_data, 'secondary_price',
                                                         'currency_code')
        self.shipping_carrier_id = parse_value(shipping_profile_upgrade_data, 'shipping_carrier_id')
        self.mail_class = parse_value(shipping_profile_upgrade_data, 'mail_class')
        self.min_delivery_days = parse_value(shipping_profile_upgrade_data, 'min_delivery_days')
        self.max_delivery_days = parse_value(shipping_profile_upgrade_data, 'max_delivery_days')


class EtsyListingSpace:
    def __init__(self, listing_data: Dict):
        self.listing_id = parse_value(listing_data, 'listing_id')
        self.user_id = parse_value(listing_data, 'user_id')
        self.shop_id = parse_value(listing_data, 'shop_id')
        self.title = parse_value(listing_data, 'title')
        self.description = parse_value(listing_data, 'description')
        self.state = Etsy.ListingState(parse_value(listing_data, 'state').lower()) if parse_value(
            listing_data, 'state') is not None else None
        self.creation_timestamp = datetime.utcfromtimestamp(parse_value(listing_data, 'creation_timestamp')
                                                            ) if parse_value(
            listing_data, 'creation_timestamp') is not None else None
        self.created_timestamp = datetime.utcfromtimestamp(parse_value(listing_data, 'created_timestamp')
                                                           ) if parse_value(
            listing_data, 'created_timestamp') is not None else None
        self.ending_timestamp = datetime.utcfromtimestamp(parse_value(listing_data, 'ending_timestamp')
                                                          ) if parse_value(
            listing_data, 'ending_timestamp') is not None else None
        self.original_creation_timestamp = datetime.utcfromtimestamp(
            parse_value(listing_data, 'original_creation_timestamp')) if parse_value(
            listing_data, 'original_creation_timestamp') is not None else None
        self.last_modified_timestamp = datetime.utcfromtimestamp(parse_value(listing_data, 'last_modified_timestamp')
                                                                 ) if parse_value(
            listing_data, 'last_modified_timestamp') is not None else None
        self.updated_timestamp = datetime.utcfromtimestamp(parse_value(listing_data, 'updated_timestamp')
                                                           ) if parse_value(
            listing_data, 'updated_timestamp') is not None else None
        self.state_timestamp = datetime.utcfromtimestamp(parse_value(listing_data, 'state_timestamp')
                                                         ) if parse_value(
            listing_data, 'state_timestamp') is not None else None
        self.quantity = parse_value(listing_data, 'quantity')
        self.shop_section_id = parse_value(listing_data, 'shop_section_id')
        self.featured_rank = parse_value(listing_data, 'featured_rank')
        self.url = parse_value(listing_data, 'url')
        self.num_favorers = parse_value(listing_data, 'num_favorers')
        self.non_taxable = parse_value(listing_data, 'non_taxable')
        self.is_taxable = parse_value(listing_data, 'is_taxable')
        self.is_customizable = parse_value(listing_data, 'is_customizable')
        self.is_personalizable = parse_value(listing_data, 'is_personalizable')
        self.personalization_is_required = parse_value(listing_data, 'personalization_is_required')
        self.personalization_char_count_max = parse_value(listing_data, 'personalization_char_count_max')
        self.personalization_instructions = parse_value(listing_data, 'personalization_instructions')
        self.listing_type = Etsy.ListingType(parse_value(listing_data, 'listing_type').lower()) if parse_value(
            listing_data, 'listing_type') is not None else None
        self.tags = list_string_encode(parse_value(listing_data, 'tags'))
        self.materials = list_string_encode(parse_value(listing_data, 'materials'))
        self.shipping_profile_id = parse_value(listing_data, 'shipping_profile_id')
        self.return_policy_id = parse_value(listing_data, 'return_policy_id')
        self.processing_min = parse_value(listing_data, 'processing_min')
        self.processing_max = parse_value(listing_data, 'processing_max')
        self.who_made = parse_value(listing_data, 'who_made')
        self.when_made = parse_value(listing_data, 'when_made')
        self.is_supply = parse_value(listing_data, 'is_supply')
        self.item_weight = parse_value(listing_data, 'item_weight')
        self.item_weight_unit = Etsy.ItemWeightUnit(parse_value(listing_data, 'item_weight_unit').lower()) if \
            parse_value(listing_data, 'item_weight_unit') is not None else Etsy.ItemWeightUnit.NONE
        self.item_length = parse_value(listing_data, 'item_length')
        self.item_height = parse_value(listing_data, 'item_height')
        self.item_width = parse_value(listing_data, 'item_width')
        self.item_dimensions_unit = Etsy.ItemDimensionsUnit(parse_value(
            listing_data, 'item_dimensions_unit').lower()) if parse_value(
            listing_data, 'item_dimensions_unit') is not None else Etsy.ItemDimensionsUnit.NONE
        self.is_private = parse_value(listing_data, 'is_private')
        self.style = list_string_encode(parse_value(listing_data, 'style'))
        self.file_data = parse_value(listing_data, 'file_data')
        self.has_variations = parse_value(listing_data, 'has_variations')
        self.should_auto_renew = parse_value(listing_data, 'should_auto_renew')
        self.language = parse_value(listing_data, 'language')
        self.price = parse_value(listing_data, 'price', 'amount')
        self.price_divisor = parse_value(listing_data, 'price', 'divisor')
        self.price_currency_code = parse_value(listing_data, 'price', 'currency_code')
        self.taxonomy_id = parse_value(listing_data, 'taxonomy_id')
        self.shipping_profile = parse_value(listing_data, 'shipping_profile')
        self.user = parse_value(listing_data, 'user')
        self.shop = parse_value(listing_data, 'shop')
        self.images = parse_value(listing_data, 'images')
        self.videos = parse_value(listing_data, 'videos')
        self.inventory = parse_value(listing_data, 'inventory')
        self.production_partners = parse_value(listing_data, 'production_partners')
        self.skus = list_string_encode(parse_value(listing_data, 'skus'))
        self.translations = parse_value(listing_data, 'translations')
        self.views = parse_value(listing_data, 'views')


class EtsyReturnPolicySpace:
    def __init__(self, return_policy_data: Dict):
        self.return_policy_id = parse_value(return_policy_data, 'return_policy_id')
        self.shop_id = parse_value(return_policy_data, 'shop_id')
        self.accepts_returns = parse_value(return_policy_data, 'accepts_returns')
        self.accepts_exchanges = parse_value(return_policy_data, 'accepts_exchanges')
        self.return_deadline = parse_value(return_policy_data, 'return_deadline')


class EtsyShopSectionSpace:
    def __init__(self, shop_section_data: Dict):
        self.shop_section_id = parse_value(shop_section_data, 'shop_section_id')
        self.title = parse_value(shop_section_data, 'title')
        self.rank = parse_value(shop_section_data, 'rank')
        self.user_id = parse_value(shop_section_data, 'user_id')
        self.active_listing_count = parse_value(shop_section_data, 'active_listing_count')


class EtsyProductionPartnerSpace:
    def __init__(self, production_partner: Dict):
        self.production_partner_id = parse_value(production_partner, 'production_partner_id')
        self.partner_name = parse_value(production_partner, 'partner_name')
        self.location = parse_value(production_partner, 'location')


class EtsyShopSpace:
    def __init__(self, etsy_shop_data: Dict):
        self.shop_id = parse_value(etsy_shop_data, 'shop_id')
        self.user_id = parse_value(etsy_shop_data, 'user_id')
        self.shop_name = parse_value(etsy_shop_data, 'shop_name')
        self.create_date = datetime.utcfromtimestamp(parse_value(etsy_shop_data, 'create_date')
                                                     ) if parse_value(
            etsy_shop_data, 'create_date') is not None else None
        self.title = parse_value(etsy_shop_data, 'title')
        self.announcement = parse_value(etsy_shop_data, 'announcement')
        self.currency_code = parse_value(etsy_shop_data, 'currency_code')
        self.is_vacation = parse_value(etsy_shop_data, 'is_vacation')
        self.vacation_message = parse_value(etsy_shop_data, 'vacation_message')
        self.sale_message = parse_value(etsy_shop_data, 'sale_message')
        self.digital_sale_message = parse_value(etsy_shop_data, 'digital_sale_message')
        self.update_date = datetime.utcfromtimestamp(parse_value(etsy_shop_data, 'update_date')
                                                     ) if parse_value(
            etsy_shop_data, 'update_date') is not None else None
        self.updated_timestamp = datetime.utcfromtimestamp(parse_value(etsy_shop_data, 'updated_timestamp')
                                                           ) if parse_value(
            etsy_shop_data, 'updated_timestamp') is not None else None
        self.listing_active_count = parse_value(etsy_shop_data, 'listing_active_count')
        self.digital_listing_count = parse_value(etsy_shop_data, 'digital_listing_count')
        self.login_name = parse_value(etsy_shop_data, 'login_name')
        self.accepts_custom_requests = parse_value(etsy_shop_data, 'accepts_custom_requests')
        self.policy_welcome = parse_value(etsy_shop_data, 'policy_welcome')
        self.policy_payment = parse_value(etsy_shop_data, 'policy_payment')
        self.policy_shipping = parse_value(etsy_shop_data, 'policy_shipping')
        self.policy_refunds = parse_value(etsy_shop_data, 'policy_refunds')
        self.policy_additional = parse_value(etsy_shop_data, 'policy_additional')
        self.policy_seller_info = parse_value(etsy_shop_data, 'policy_seller_info')
        self.policy_update_date = datetime.utcfromtimestamp(parse_value(etsy_shop_data, 'policy_update_date')
                                                            ) if parse_value(
            etsy_shop_data, 'policy_update_date') is not None else None
        self.policy_has_private_receipt_info = parse_value(etsy_shop_data, 'policy_has_private_receipt_info')
        self.has_unstructured_policies = parse_value(etsy_shop_data, 'has_unstructured_policies')
        self.policy_privacy = parse_value(etsy_shop_data, 'policy_privacy')
        self.vacation_autoreply = parse_value(etsy_shop_data, 'vacation_autoreply')
        self.url = parse_value(etsy_shop_data, 'url')
        self.image_url_760x100 = parse_value(etsy_shop_data, 'image_url_760x100')
        self.num_favorers = parse_value(etsy_shop_data, 'num_favorers')
        self.languages = list_string_encode(parse_value(etsy_shop_data, 'languages'))
        self.icon_url_fullxfull = parse_value(etsy_shop_data, 'icon_url_fullxfull')
        self.is_using_structured_policies = parse_value(etsy_shop_data, 'is_using_structured_policies')
        self.has_onboarded_structured_policies = parse_value(etsy_shop_data, 'has_onboarded_structured_policies')
        self.include_dispute_form_link = parse_value(etsy_shop_data, 'include_dispute_form_link')
        self.is_etsy_payments_onboarded = parse_value(etsy_shop_data, 'is_etsy_payments_onboarded')
        self.is_calculated_eligible = parse_value(etsy_shop_data, 'is_calculated_eligible')
        self.is_opted_into_buyer_promise = parse_value(etsy_shop_data, 'is_opted_in_to_buyer_promise')
        self.is_shop_us_based = parse_value(etsy_shop_data, 'is_shop_us_based')
        self.transaction_sold_count = parse_value(etsy_shop_data, 'transaction_sold_count')
        self.shipping_from_country_iso = parse_value(etsy_shop_data, 'shipping_from_country_iso')
        self.shop_location_country_iso = parse_value(etsy_shop_data, 'shop_location_country_iso')
        self.review_count = parse_value(etsy_shop_data, 'review_count')
        self.review_average = parse_value(etsy_shop_data, 'review_average')


class EtsyOfferingSpace:
    def __init__(self, offering_data: Dict):
        self.offering_id = parse_value(offering_data, 'offering_id')
        self.quantity = parse_value(offering_data, 'quantity')
        self.is_enabled = parse_value(offering_data, 'is_enabled')
        self.is_deleted = parse_value(offering_data, 'is_deleted')
        self.price = parse_value(offering_data, 'price', 'amount')
        self.price_divisor = parse_value(offering_data, 'price', 'divisor')
        self.price_currency_code = parse_value(offering_data, 'price', 'currency_code')


class EtsyRefundSpace:
    def __init__(self, refund_data: Dict):
        self.amount = parse_value(refund_data, 'amount', 'amount')
        self.amount_divisor = parse_value(refund_data, 'amount', 'divisor')
        self.amount_currency_code = parse_value(refund_data, 'amount', 'currency_code')
        self.created_timestamp = datetime.utcfromtimestamp(parse_value(refund_data, 'created_timestamp')
                                                           ) if parse_value(
            refund_data, 'created_timestamp') is not None else None
        self.reason = parse_value(refund_data, 'reason')
        self.note_from_issuer = parse_value(refund_data, 'note_from_issuer')
        self.status = parse_value(refund_data, 'status')


class ProdigiOrderSpace:
    def __init__(self, order_data: Dict):
        print(order_data)
        self.prodigi_id = parse_value(order_data, 'id')
        self.created = prodigi_timestamp_to_datetime(parse_value(order_data, 'created').split('.')[0]) if parse_value(
            order_data, 'created') is not None else None
        self.last_updated = prodigi_timestamp_to_datetime(parse_value(order_data, 'lastUpdated').split('.')[0]) if \
            parse_value(order_data, 'lastUpdated') is not None else None
        self.callback_url = parse_value(order_data, 'callbackUrl')
        self.merchant_reference = parse_value(order_data, 'merchantReference')
        self.shipping_method = Prodigi.ShippingMethod(parse_value(order_data, 'shippingMethod').lower()) if \
            parse_value(order_data, 'shippingMethod') is not None else None
        self.idempotency_key = parse_value(order_data, 'idempotencyKey')
        self.status = parse_value(order_data, 'status')
        self.charges = parse_value(order_data, 'charges')
        self.shipments = parse_value(order_data, 'shipments')
        self.recipient = parse_value(order_data, 'recipient')
        self.items = parse_value(order_data, 'items')
        self.packing_slip = parse_value(order_data, 'packingSlip')
        self.metadata = parse_value(order_data, 'metadata')


class ProdigiStatusSpace:
    def __init__(self, status_data: Dict):
        self.stage = Prodigi.StatusStage(parse_value(status_data, 'stage').lower()) if parse_value(
            status_data, 'stage') is not None else None
        self.download_assets = Prodigi.DetailStatus(parse_value(status_data, 'details', 'downloadAssets').lower()) if \
            parse_value(status_data, 'details', 'downloadAssets') is not None else None
        self.print_ready_assets_prepared = Prodigi.DetailStatus(
            parse_value(status_data, 'details', 'printReadyAssetsPrepared').lower()) if \
            parse_value(status_data, 'details', 'printReadyAssetsPrepared') is not None else None
        self.allocate_production_location = Prodigi.DetailStatus(
            parse_value(status_data, 'details', 'allocateProductionLocation').lower()) if \
            parse_value(status_data, 'details', 'allocateProductionLocation') is not None else None
        self.in_production = Prodigi.DetailStatus(parse_value(status_data, 'details', 'inProduction').lower()) if \
            parse_value(status_data, 'details', 'inProduction') is not None else None
        self.shipping = Prodigi.DetailStatus(parse_value(status_data, 'details', 'shipping').lower()) if \
            parse_value(status_data, 'details', 'shipping') is not None else None
        self.issues = parse_value(status_data, 'issues')


class ProdigiIssueSpace:
    def __init__(self, issue_data: Dict):
        self.object_id = parse_value(issue_data, 'objectId')
        self.error_code = Prodigi.IssueErrorCode(parse_value(issue_data, 'errorCode').lower()) if parse_value(
            issue_data, 'errorCode') is not None else None
        self.description = parse_value(issue_data, 'description')
        self.authorization_details = parse_value(issue_data, 'authorisationDetails')


class ProdigiAuthorizationDetailsSpace:
    def __init__(self, authorization_details_data: Dict):
        self.authorization_url = parse_value(authorization_details_data, 'authorisationUrl')
        self.payment_details = parse_value(authorization_details_data, 'paymentDetails')


class ProdigiCostSpace:
    def __init__(self, cost_data: Dict):
        self.amount = parse_value(cost_data, 'amount')
        self.currency = parse_value(cost_data, 'currency')


class ProdigiChargeSpace:
    def __init__(self, charge_data: Dict):
        self.prodigi_id = parse_value(charge_data, 'id')
        self.prodigi_invoice_number = parse_value(charge_data, 'prodigiInvoiceNumber')
        self.total_cost = parse_value(charge_data, 'totalCost')
        self.items = parse_value(charge_data, 'items')


class ProdigiChargeItemSpace:
    def __init__(self, charge_item_data: Dict):
        self.prodigi_id = parse_value(charge_item_data, 'id')
        self.description = parse_value(charge_item_data, 'description') if 'description' in charge_item_data else None
        self.item_sku = parse_value(charge_item_data, 'itemSku') if 'itemSku' in charge_item_data else None
        self.shipment_id = parse_value(charge_item_data, 'shipmentId')
        self.item_id = parse_value(charge_item_data, 'itemId')
        self.merchant_item_reference = parse_value(charge_item_data,
            'merchantItemReference') if 'merchantItemReference' in charge_item_data else None
        self.cost = parse_value(charge_item_data, 'cost')


class ProdigiShipmentSpace:
    def __init__(self, shipment_data: Dict):
        self.prodigi_id = parse_value(shipment_data, 'id')
        self.carrier_name = parse_value(shipment_data, 'carrier', 'name')
        self.carrier_service = parse_value(shipment_data, 'carrier', 'service')
        self.service = parse_value(shipment_data, 'carrier', 'service')
        self.tracking_number = parse_value(shipment_data, 'tracking', 'number')
        self.tracking_url = parse_value(shipment_data, 'tracking', 'url')
        self.dispatch_date = prodigi_timestamp_to_datetime(parse_value(
            shipment_data, 'dispatchDate').split('.')[0]) if parse_value(
            shipment_data, 'dispatchDate') is not None else None
        self.items = parse_value(shipment_data, 'items')
        self.fulfillment_location = parse_value(shipment_data, 'fulfillmentLocation')


class ProdigiFulfillmentLocationSpace:
    def __init__(self, fulfillment_location_data: Dict):
        self.country_code = parse_value(fulfillment_location_data, 'countryCode')
        self.lab_code = parse_value(fulfillment_location_data, 'labCode')


class ProdigiShipmentItemSpace:
    def __init__(self, shipment_item_data: Dict):
        self.item_id = parse_value(shipment_item_data, 'itemId')


class ProdigiRecipientSpace:
    def __init__(self, recipient_data: Dict):
        self.name = parse_value(recipient_data, 'name')
        self.email = parse_value(recipient_data, 'email')
        self.phone_number = parse_value(recipient_data, 'phoneNumber')
        self.address = parse_value(recipient_data, 'address')


class ProdigiAddressSpace:
    def __init__(self, address_data: Dict):
        self.first_line = parse_value(address_data, 'line1')
        self.second_line = parse_value(address_data, 'line2')
        self.zip = parse_value(address_data, 'postalOrZipCode')
        self.country = parse_value(address_data, 'countryCode')
        self.city = parse_value(address_data, 'townOrCity')
        self.state = parse_value(address_data, 'stateOrCounty')


class ProdigiItemSpace:
    def __init__(self, item_data: Dict):
        self.prodigi_id = parse_value(item_data, 'id')
        self.merchant_reference = parse_value(item_data, 'merchantReference')
        self.sku = parse_value(item_data, 'sku')
        self.copies = parse_value(item_data, 'copies')
        self.sizing = Prodigi.Sizing(parse_value(item_data, 'sizing').lower())
        self.recipient_cost = parse_value(item_data, 'recipientCost')
        self.attributes = parse_value(item_data, 'attributes')
        self.assets = parse_value(item_data, 'assets')


class ProdigiAssetSpace:
    def __init__(self, asset_data: Dict):
        self.print_area = parse_value(asset_data, 'printArea')
        self.url = parse_value(asset_data, 'url')


class ProdigiPackingSlipSpace:
    def __init__(self, packing_slip_data: Dict):
        self.url = parse_value(packing_slip_data, 'url')
        self.status = parse_value(packing_slip_data, 'status')


class ProdigiShipmentDetailSpace:
    def __init__(self, shipment_detail_data: Dict):
        self.shipment_id = parse_value(shipment_detail_data, 'shipmentId')
        self.successful = parse_value(shipment_detail_data, 'successful')
        self.error_code = Prodigi.ShipmentUpdateErrorCode(parse_value(shipment_detail_data, 'errorCode').lower())
        self.description = parse_value(shipment_detail_data, 'description')
