import os
import json
import requests
from database.tables import Address, EtsyBuyer, EtsyProduct, EtsyOffering, EtsySeller, EtsyTransaction

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


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

    def place_order(self, address: Address, transaction: EtsyTransaction):
        url = "https://api.sandbox.prodigi.com/v4.0/Orders"

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        # TODO: Use transaction SKU to get prodigi SKU
        sku = transaction.product.sku.split('%')[-1]

        # TODO: Map the shipping upgrades if we are going to do that
        shipping_method = 'Budget' if transaction.shipping_upgrade is None else transaction.shipping_upgrade

        body = {
            "shippingMethod": shipping_method,
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
            "items": [{
                "sku": sku,
                "copies": transaction.quantity,
                "sizing": "fillPrintArea",
                "assets": [
                    {
                        "printArea": "default",
                        "url": "https://your-image-url/image.png"
                    }
                ]
            }]
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())
