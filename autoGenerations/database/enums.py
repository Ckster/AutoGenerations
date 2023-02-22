import enum


class TransactionFulfillmentStatus(enum.Enum):
    NEEDS_FULFILLMENT = 'needs_fulfillment'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    ORDER_CANCELED = 'order_canceled'


class OrderStatus(enum.Enum):
    INCOMPLETE = 'incomplete'
    COMPLETE = 'complete'
    CANCELED = 'canceled'


class Prodigi:
    class ShippingMethod(enum.Enum):
        BUDGET = "Budget"
        STANDARD = "Standard"
        EXPRESS = "Express"
        OVERNIGHT = "Overnight"

    class StatusStage(enum.Enum):
        IN_PROGRESS = "InProgress"
        COMPLETE = "Complete"
        CANCELLED = "Cancelled"

    class DetailStatus(enum.Enum):
        NOT_STARTED = "NotStarted"
        IN_PROGRESS = "InProgress"
        COMPLETE = "Complete"
        ERROR = "Error"

    class IssueErrorCode(enum.Enum):
        NOT_DOWNLOADED = "order.items.assets.NotDownloaded"
        FAILED_TO_DOWNLOAD = "order.items.assets.FailedToDownloaded"
        ITEM_UNAVAILABLE = "order.items.assets.ItemUnavailable"

    class Sizing(enum.Enum):
        FILL_PRINT_AREA = 'fillPrintArea'
        FIT_PRINT_AREA = 'fitPrintArea'
        STRETCH_TO_PRINT_AREA = 'stretchToPrintArea'

    class CreateOrderOutcome(enum.Enum):
        CREATED = "created"
        CREATED_WITH_ISSUES = "createdWithIssues"
        ALREADY_EXISTS = "alreadyExists"

    class GetOrderOutcome(enum.Enum):
        OK = "ok"

    class GeneralOutcome(enum.Enum):
        VALIDATION_FAILED = "validationFailed"
        ENTITY_NOT_FOUND = "entityNotFound"
        ENDPOINT_DOES_NOT_EXIST = "endpointDoesNotExist"
        METHOD_NOT_ALLOWED = "methodNotAllowed"
        INVALID_CONTENT_TYPE = "invalidContentType"
        INTERNAL_SERVER_ERROR = "internalServerError"
        TIMED_OUT = "timedOut"

    class OrderStatus(enum.Enum):
        DRAFT = "draft"
        AWAITING_PAYMENT = "awaitingPayment"
        IN_PROGRESS = "inProgress"
        COMPLETE = "complete"
        CANCELLED = "cancelled"

    class CancelOrderOutcome(enum.Enum):
        CANCELLED = "cancelled"
        FAILED_TO_CANCEL = "failedToCancel"
        ACTION_NOT_AVAILABLE = "actionNotAvailable"

    class ShipmentUpdateErrorCode(enum.Enum):
        UPDATE_FAILED = "order.shipments.updateFailed"
        INVALID = "order.shipments.invalid"
        NOT_AVAILABLE = "order.shipments.notAvailable"

    class UpdateShippingMethodOutcome(enum.Enum):
        UPDATED = "updated"
        PARTIALLY_UPDATED = "partiallyUpdated"
        FAILED_TO_UPDATE = "failedToUpdate"
        ACTION_NOT_AVAILABLE = "actionNotAvailable"

    class UpdateRecipientOutcome(enum.Enum):
        UPDATED = "updated"
        PARTIALLY_UPDATED = "partiallyUpdated"
        FAILED_TO_UPDATE = "failedToUpdate"
        ACTION_NOT_AVAILABLE = "actionNotAvailable"

    class UpdateRecipientResponse(enum.Enum):
        COMPLETED = "completed"
        PARTIALLY_COMPLETE = "partiallyComplete"
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
