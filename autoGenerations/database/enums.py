import enum


class OrderStatus:
    NEEDS_FULFILLMENT = 'needs_fulfillment'
    FULFILLMENT_STARTED = 'fulfillment_started'
    FULFILLED = 'fulfilled'
    CANCELED = 'canceled'


class Etsy:
    class OrderStatus(enum.Enum):
        PAID = "paid"
        COMPLETED = "completed"
        OPEN = "open"
        PAYMENT_PROCESSING = "payment_processing"
        CANCELED = "canceled"
