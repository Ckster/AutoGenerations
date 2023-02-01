from typing import Dict


class EtsyReceiptSpace:
    def __init__(self, receipt: Dict):
        self.receipt_id = receipt['receipt_id']
        self.receipt_type = receipt['receipt_type']
        self.buyer_user_id = receipt['buyer_user_id']
        self.buyer_email = receipt['buyer_email']
        self.seller_user_id = receipt['seller_user_id']
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
        self.country = receipt['country']
        self.first_line = receipt['first_line']
        self.second_line = receipt['second_line']
        self.formattd = receipt['formatted']


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
