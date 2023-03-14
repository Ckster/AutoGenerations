import enum


class OrderStatus(enum.Enum):
    INCOMPLETE = 'incomplete'
    COMPLETE = 'complete'
    CANCELED = 'canceled'


class Prodigi:
    class ShippingMethod(enum.Enum):
        BUDGET = "budget"
        STANDARD = "standard"
        EXPRESS = "express"
        OVERNIGHT = "overnight"

    class StatusStage(enum.Enum):
        IN_PROGRESS = "inprogress"
        COMPLETE = "complete"
        CANCELLED = "cancelled"

    class DetailStatus(enum.Enum):
        NOT_STARTED = "notstarted"
        IN_PROGRESS = "inprogress"
        COMPLETE = "complete"
        ERROR = "error"

    class IssueErrorCode(enum.Enum):
        NOT_DOWNLOADED = "order.items.assets.notdownloaded"
        FAILED_TO_DOWNLOAD = "order.items.assets.failedtodownloaded"
        ITEM_UNAVAILABLE = "order.items.assets.itemunavailable"

    class Sizing(enum.Enum):
        FILL_PRINT_AREA = 'fillprintarea'
        FIT_PRINT_AREA = 'fitprintarea'
        STRETCH_TO_PRINT_AREA = 'stretchtoprintarea'

    class CreateOrderOutcome(enum.Enum):
        CREATED = "created"
        CREATED_WITH_ISSUES = "createdwithissues"
        ALREADY_EXISTS = "alreadyexists"

    class GetOrderOutcome(enum.Enum):
        OK = "ok"

    class GeneralOutcome(enum.Enum):
        VALIDATION_FAILED = "validationfailed"
        ENTITY_NOT_FOUND = "entitynotfound"
        ENDPOINT_DOES_NOT_EXIST = "endpointdoesnotexist"
        METHOD_NOT_ALLOWED = "methodnotallowed"
        INVALID_CONTENT_TYPE = "invalidcontenttype"
        INTERNAL_SERVER_ERROR = "internalservererror"
        TIMED_OUT = "timedout"

    class OrderStatus(enum.Enum):
        DRAFT = "draft"
        AWAITING_PAYMENT = "awaitingpayment"
        IN_PROGRESS = "inprogress"
        COMPLETE = "complete"
        CANCELLED = "cancelled"

    class CancelOrderOutcome(enum.Enum):
        CANCELLED = "cancelled"
        FAILED_TO_CANCEL = "failedtocancel"
        ACTION_NOT_AVAILABLE = "actionnotavailable"

    class ShipmentUpdateErrorCode(enum.Enum):
        UPDATE_FAILED = "order.shipments.updatefailed"
        INVALID = "order.shipments.invalid"
        NOT_AVAILABLE = "order.shipments.notavailable"

    class UpdateShippingMethodOutcome(enum.Enum):
        UPDATED = "updated"
        PARTIALLY_UPDATED = "partiallyupdated"
        FAILED_TO_UPDATE = "failedtoupdate"
        ACTION_NOT_AVAILABLE = "actionnotavailable"

    class UpdateRecipientOutcome(enum.Enum):
        UPDATED = "updated"
        PARTIALLY_UPDATED = "partiallyupdated"
        FAILED_TO_UPDATE = "failedtoupdate"
        ACTION_NOT_AVAILABLE = "actionnotavailable"

    class UpdateRecipientResponse(enum.Enum):
        COMPLETED = "completed"
        PARTIALLY_COMPLETE = "partiallycomplete"
        FAILED = "failed"


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
        EDIT = "edit"

    class ListingType(enum.Enum):
        PHYSICAL = "physical"
        DOWNLOAD = "download"
        BOTH = "both"

    class ItemWeightUnit(enum.Enum):
        OUNCE = "oz"
        POUND = "lb"
        GRAM = "g"
        KILOGRAM = "kg"
        NONE = "n/a"

    class ItemDimensionsUnit(enum.Enum):
        INCH = "in"
        FEET = "ft"
        MILLIMETER = "mm"
        CENTIMETER = "cm"
        METER = "m"
        YARD = "yd"
        INCHES = "inches"  # Yeah idk
        NONE = "n/a"

    class ShippingProfileType(enum.Enum):
        MANUAL = "manual"
        CALCULATED = "calculated"

    class ShippingUpgradeType(enum.Enum):
        DOMESTIC = 0
        INTERNATIONAL = 1
