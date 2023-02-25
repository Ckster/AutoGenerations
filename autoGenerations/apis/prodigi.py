import os
import json
import requests
from typing import List, Dict
from database.etsy_tables import Address, EtsyBuyer, EtsyProduct, EtsyOffering, EtsySeller, EtsyTransaction
from database.prodigi_tables import ProdigiRecipient
from database.enums import Prodigi

from datetime import datetime

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))

# TODO: Change in production
BASE_URL = "https://api.sandbox.prodigi.com/v4.0/"
# production URL is https://api.prodigi.com/v4.0


class Secrets:

    def __init__(self):
        self._secrets_path = os.path.join(PROJECT_DIR, 'prodigy_secrets.json')
        if not os.path.exists(self._secrets_path):
            raise FileNotFoundError('Could not find prodigy_secrets.json file in project')

        self._sandbox_key = None
        self._prod_key = None
        with open(self._secrets_path, 'r') as f:
            secrets = json.load(f)
            self._sandbox_key = secrets['sandbox_access_key']
            self._prod_key = secrets['prod_access_key']

    @property
    def sandbox_key(self):
        return self._sandbox_key

    @property
    def prod_key(self):
        return self._prod_key


class API(Secrets):
    def __init__(self, sandbox_mode: bool = True):
        super(API, self).__init__()
        self.access_key = self.sandbox_key if sandbox_mode else self.prod_key

    def create_order(self, address: Address, transaction: EtsyTransaction, items: List[Dict[str, str]]):
        """
        API Reference: https://www.prodigi.com/print-api/docs/reference/#create-order
        :param address:
        :param transaction:
        :return:
        """
        url = os.path.join(BASE_URL, "orders")

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        # TODO: Map the shipping upgrades if we are going to do that
        shipping_method = 'Budget' if transaction.shipping_upgrade is None else transaction.shipping_upgrade

        # TODO: Create a unique key for this order so prodigi can detect duplicate orders
        idempotency_key = None

        body = {
            "shippingMethod": shipping_method,
            "idempotencyKey": idempotency_key,
            "recipient": {
                "address": {
                    "line1":  address.first_line,
                    "line2": address.second_line,
                    "postalOrZipCode": address.zip_code,
                    "countryCode": address.country,
                    "townOrCity": address.city,
                    "stateOrCounty": address.state
                },

                "name": transaction.buyer.name,
                "email": transaction.seller.email
            },
            "items": items
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_order(self, order_id: str):
        """
        API Reference: https://www.prodigi.com/print-api/docs/reference/#get-order-by-id
        :return:
        """
        url = os.path.join(BASE_URL, "order", order_id)

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_orders(self, top: int = None, skip: int = None, created_from: datetime = None, created_to: datetime = None,
                   status: Prodigi.OrderStatus = None, order_ids: List[str] = None,
                   merchant_references: List[str] = None):
        """
        API Reference: https://www.prodigi.com/print-api/docs/reference/#get-orders
        :return:
        """
        url = os.path.join(BASE_URL, "orders")

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        params = {}
        if top is not None:
            params['top'] = top
        if skip is not None:
            params['skip'] = skip
        if created_from is not None:
            params['createdFrom'] = created_from
        if created_to is not None:
            params['createdTo'] = created_to
        if status is not None:
            params['status'] = status.value
        if order_ids is not None:
            params['orderIds'] = order_ids
        if merchant_references is not None:
            params['merchantReferences'] = merchant_references

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_order_actions(self, order_id: str):
        """
        API Reference: https://www.prodigi.com/print-api/docs/reference/#get-actions
        :param order_id:
        :return:
        """
        url = os.path.join(BASE_URL, "orders", order_id, "actions")

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def cancel_order(self, order_id: str):
        """
        API Reference: https://www.prodigi.com/print-api/docs/reference/#cancel-an-order
        :param order_id:
        :return:
        """
        url = os.path.join(BASE_URL, "orders", order_id, "actions", "cancel")

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def update_shipping(self, order_id: str, new_shipping_method: Prodigi.ShippingMethod):
        """
        API Reference: https://www.prodigi.com/print-api/docs/reference/#cancel-an-order
        Args:
            order_id (str):
            new_shipping_method (Prodigi.ShippingMethod):
        :return:
        """
        url = os.path.join(BASE_URL, "orders", order_id, "actions", "updateShippingMethod")

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        body = {'shippingMethod': new_shipping_method.value}

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def update_recipient(self, order_id: str, new_recipient: ProdigiRecipient, address: Address):
        """
        API Reference: https://www.prodigi.com/print-api/docs/reference/#update-recipient
        :param order_id:
        :param new_recipient:
        :return:
        """
        url = os.path.join(BASE_URL, "orders", order_id, "actions", "updateRecipient")

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        body = {
            'name': new_recipient.name,
            'email': new_recipient.email,
            'phoneNumber': new_recipient.phone_number,
            'address': {
                'line1': address.first_line,
                'line2': address.second_line,
                'postalOrZipCode': address.zip_code,
                'countryCode': address.country,
                'townOrCity': address.city,
                'stateOrCounty': address.state
            }
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_quote(self,  items: List[Dict[str]],
                  shipping_method: Prodigi.ShippingMethod = Prodigi.ShippingMethod.BUDGET,
                  destination_country: str = 'US', currency_code: str = 'USD'):
        url = os.path.join(BASE_URL, "quotes")

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        body = {
            'shippingMethod': shipping_method.value,
            'destinationCountryCode': destination_country,
            'currencyCode': currency_code,
            "items": items
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_product_details(self, sku):
        """
        API Reference: https://www.prodigi.com/print-api/docs/reference/#get-product-details
        :param sku:
        :return:
        """
        url = os.path.join(BASE_URL, "quotes", sku)

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())