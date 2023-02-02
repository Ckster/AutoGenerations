import os
import json
import requests
from typing import Dict

from apis.enums import Carrier

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


class Secrets:

    def __init__(self):
        self._secrets_path = os.path.join(PROJECT_DIR, 'etsy_secrets.json')
        if not os.path.exists(self._secrets_path):
            raise FileNotFoundError('Could not find etsy_secrets.json file in project')

        self._store_id = None
        self._shared_secret = None
        self._keystring = None
        self._refresh_token = None
        self._access_token = None
        with open(self._secrets_path, 'r') as f:
            secrets = json.load(f)
            self._store_id = secrets['store_id']
            self._shared_secret = secrets['shared_secret']
            self._keystring = secrets['keystring']
            self._access_token = secrets['access_token']
            self._refresh_token = secrets['refresh_token']

    @property
    def keystring(self):
        return self._keystring

    @property
    def shared_secret(self):
        return self._shared_secret

    @property
    def store_id(self):
        return self._store_id

    @property
    def refresh_token(self):
        return self._refresh_token


class API(Secrets):
    BASE_ETSY_URL = 'https://api.etsy.com/v3'
    BASE_SERVER_URL = 'http://localhost:3003/'

    def __init__(self):
        super(API, self).__init__()

    def _ping(self):
        """
        This just requests data from the api ping endpoint so connection can be tested. If the ping is not successful
        then the error message can be used to determine how to correct the connection, i.e. refresh the token, wait a
        period of time, or email a human.
        """
        url = 'https://api.etsy.com/v3/application/openapi-ping'
        headers = {
                'x-api-key': self._keystring,
            }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    # TODO: Authentication errors return a 401 code. When the scoped request class is made add that in to
    #  get_new_access_token

    def _get_new_access_token(self):
        """
        Requests a new access token and refresh token and updates the secrets.json file with them. Each access token is
        valid for 1 hour, but the refresh token that comes with it can be used to generate a new access token. Refresh
        tokens are valid for 90 days, and you get a new refresh token with each new access token.
        """
        url = 'https://api.etsy.com/v3/public/oauth/token'
        headers = {
            'Content-Type': 'application/json'
        }
        body = {
                'grant_type': 'refresh_token',
                'client_id': self._keystring,
                'refresh_token': self._refresh_token
            }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            data = response.json()
            new_access_token = data['access_token']
            new_refresh_token = data['refresh_token']

            with open(self._secrets_path, 'r') as f:
                secrets = json.load(f)

            secrets['access_token'] = new_access_token
            secrets['refresh_token'] = new_refresh_token

            self._access_token = new_access_token
            self._refresh_token = new_refresh_token

            with open(self._secrets_path, 'w') as f:
                json.dump(secrets, f)

        else:
            raise LookupError(response.json())

    def get_receipts(self):
        """

        :return:
        """
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', self.store_id, 'receipts')

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-key": self.keystring,
            "Authorization": f"Bearer {self._access_token}"
        }

        params = {
            "was_paid": "true",
            "min_last_modified": "1674166698"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_listings_by_shop_receipt(self, receipt_id: int):
        """

        :return:
        """

        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', self.store_id, 'receipts', str(receipt_id),
                           'listings')

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-key": self.keystring,
            "Authorization": f"Bearer {self._access_token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_listings(self, listing_id: int):
        """

        :return:
        """

        url = os.path.join(self.BASE_ETSY_URL, 'application', 'listings', str(listing_id))

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-key": self.keystring,
            "Authorization": f"Bearer {self._access_token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())
    def update_receipt(self, receipt_id: str, body: Dict[str, str]):
        """

        :return:
        """
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', self.store_id, 'receipts', receipt_id)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-key": self.keystring,
            "Authorization": f"Bearer {self._access_token}"
        }

        response = requests.put(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def update_order_tracking(self, order_id: str, carrier: Carrier, tracking_code: str, note_to_buyer: str,
                              send_bcc: bool = True):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', self.store_id, 'receipts', order_id, 'tracking')

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-key": self.keystring,
            "Authorization": f"Bearer {self._access_token}"
        }

        body = {
            "carrier_name": carrier.name,
            "tracking_code": tracking_code,
            "send_bcc": send_bcc,
            "note_to_buyer": note_to_buyer
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())
