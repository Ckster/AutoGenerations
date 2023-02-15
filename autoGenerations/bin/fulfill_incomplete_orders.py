from database.namespaces import EtsyReceiptShipmentSpace, EtsyProductPropertySpace, EtsyListingSpace, EtsyShopSpace, \
    EtsyShopSectionSpace, EtsyReturnPolicySpace, EtsyShippingProfileSpace, EtsyProductionPartnerSpace, \
    EtsyShippingProfileUpgradeSpace, EtsyShippingProfileDestinationSpace, EtsyProductSpace
from database.utils import make_engine
from database.tables import EtsyReceipt, Address, EtsyReceiptShipment, EtsyTransaction, EtsySeller, EtsyBuyer, \
    EtsyProduct, EtsyProductProperty, EtsyListing, EtsyShop, EtsyShopSection, EtsyReturnPolicy, EtsyShippingProfile, \
    EtsyProductionPartner, EtsyShippingProfileUpgrade, EtsyShippingProfileDestination
from database.enums import Etsy as EtsyEnums, OrderStatus, TransactionFulfillmentStatus
from apis.prodigy import API

from sqlalchemy.orm import Session


# TODO: Receipts will become complete when all transactions for that receipt have been completed
def main():
    prodigy_api = API()
    with Session(make_engine()) as session:
        incomplete_receipts = session.query(EtsyReceipt).filter(
            EtsyReceipt.order_status == OrderStatus.INCOMPLETE
        ).all()

        for receipt in incomplete_receipts:

            for transaction in receipt.transactions:
                if transaction.fulfillment_status == TransactionFulfillmentStatus.NEEDS_FULFILLMENT:
                    prodigy_api.place_order()
                    pass
