import enum


class Carrier(enum.Enum):
    """
    Each carrier as it is known to Etsy. A table with all the names can be found here:
    https://developer.etsy.com/documentation/tutorials/fulfillment
    """
    FEDEX = 'fedex'
    UPS = 'ups'
    USPS = 'usps'
