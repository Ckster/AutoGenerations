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
