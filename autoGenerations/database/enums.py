import enum


class TransactionFulfillmentStatus:
    NEEDS_FULFILLMENT = 'needs_fulfillment'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ORDER_CANCELED = 'order_canceled'


class OrderStatus:
    INCOMPLETE = 'incomplete'
    COMPLETE = 'complete'
    CANCELED = 'canceled'


class Etsy:
    class OrderStatus(enum.Enum):
        PAID = "Paid"
        COMPLETED = "Completed"
        OPEN = "Open"
        PAYMENT_PROCESSING = "Payment_processing"
        CANCELED = "Canceled"

    class ListingState(enum.Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"
        SOLD_OUT = "sold_out"
        DRAFT = "draft"
        EXPIRED = "expired"

    class ListingType(enum.Enum):
        PHYSICAL = "physical"
        DOWNLOAD = "download"
        BOTH = "both"

    class ItemWeightUnit(enum.Enum):
        OUNCE = "oz"
        POUND = "lb"
        GRAM = "g"
        KILOGRAM = "kg"

    class ItemDimensionsUnit(enum.Enum):
        INCH = "in"
        FEET = "ft"
        MILLIMETER = "mm"
        CENTIMETER = "cm"
        METER = "m"
        YARD = "yd"
        INCHES = "inches"  # Yeah idk

    class ShippingProfileType(enum.Enum):
        MANUAL = "manual"
        CALCULATED = "calculated"

    class ShippingUpgradeType(enum.Enum):
        DOMESTIC = "0"
        INTERNATIONAL = "1"
