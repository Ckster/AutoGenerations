import os
import json
import requests

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

    def place_order(self):
        url = "https://api.sandbox.prodigi.com/v4.0/Orders"

        headers = {
            "X-API-Key": self.access_key,
            "Content-Type": "application/json"
        }

        body = {
            "shippingMethod": "Budget",
            "recipient": {
                "address": {
                    "line1": "3303 Bluff St",
                    "line2": "Unit 211",
                    "postalOrZipCode": "80301",
                    "countryCode": "US",
                    "townOrCity": "Boulder",
                    "stateOrCounty": "Colorado"
                },
                "name": "Erick V",
                "email": "verleyeerick@gmail.com"
            },
            "items": [{
                "sku": "GLOBAL-FAP-16x24",
                "copies": 1,
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
