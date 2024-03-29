import os
import json
import requests
from typing import Dict, Union, Any, List
from urllib.parse import urlencode


PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


class ListingNotFoundError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


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
        self._get_new_access_token()
        self._signed_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-key": self.keystring,
            "Authorization": f"Bearer {self._access_token}"
        }

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

    def create_draft_listing(self, listing_info: Dict[str, Any], shop_id):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'listings')

        header = self._signed_header
        header['Content-Type'] = 'application/json'

        response = requests.post(url, headers=header, data=json.dumps(listing_info))

        if response.status_code == 201:
            return response.json()
        else:
            raise LookupError(response.json())

    def update_listing_inventory(self, listing_id, inventory_data):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'listings', listing_id, 'inventory')

        header = self._signed_header
        header['Content-Type'] = 'application/json'

        response = requests.put(url, headers=header, data=json.dumps(inventory_data))

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def upload_listing_image(self, shop_id: str, listing_id: str, image_data: Dict[str, str]):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'listings', listing_id,
                           'images')

        header = self._signed_header
        header = {key: header[key] for key in header.keys() if key != 'Content-Type'}

        response = requests.post(url, headers=header, files=image_data)

        if response.status_code == 201:
            return response.json()
        else:
            raise LookupError(response.json())

    def upload_listing_file(self, shop_id: str, listing_id: str, file_data: Dict[str, str], name: str):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'listings', listing_id,
                           'files')

        header = self._signed_header
        header = {key: header[key] for key in header.keys() if key != 'Content-Type'}

        response = requests.post(url, headers=header, files=file_data, data={'name': name})

        if response.status_code == 201:
            return response.json()
        else:
            raise LookupError(response.json())

    def update_listing(self, shop_id: str, listing_id: str, listing_data: Dict[str, Any]):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'listings', listing_id)

        url += '&' + urlencode(listing_data)

        header = self._signed_header

        response = requests.patch(url, headers=header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def delete_listing_image(self, shop_id: str, listing_id: str, image_id: str):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'listings', listing_id,
                           'images', image_id)

        header = self._signed_header

        response = requests.delete(url, headers=header)

        if response.status_code == 204:
            return 'success'
        else:
            raise LookupError(response.json())

    def get_listing_images(self, shop_id: str, listing_id: str):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'listings', listing_id,
                           'images')

        header = self._signed_header

        response = requests.get(url, headers=header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def update_variation_images(self, shop_id, listing_id, variation_images: List[Dict[str, Any]]):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'listings', listing_id,
                           'variation-images')

        header = self._signed_header
        header['Content-Type'] = 'application/json'

        data = {
            'variation_images': variation_images
        }

        response = requests.post(url, headers=header, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_shop_return_policies(self, shop_id):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'policies', 'return')

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_receipts(self, min_created: Union[int, str] = None):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', self.store_id, 'receipts')

        params = {}
        if min_created is not None:
            params['min_created'] = str(min_created)

        response = requests.get(url, headers=self._signed_header, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_receipt(self, receipt_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', self.store_id, 'receipts', str(receipt_id))

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_listings_by_shop_receipt(self, receipt_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', self.store_id, 'receipts', str(receipt_id),
                           'listings')

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_listing(self, listing_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'listings', str(listing_id))

        response = requests.get(url, headers=self._signed_header)

        data = response.json()
        if response.status_code == 200:
            return data
        else:
            if 'error' in data and data['error'].lower() == f'Could not find a Listing with listing_id' \
                                                            f' = {listing_id}'.lower():
                return ListingNotFoundError
            else:
                raise LookupError(response.json())

    def get_listing_product(self, listing_id: int, product_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'listings', str(listing_id), 'inventory', 'products',
                           str(product_id))

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_shop(self, shop_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', str(shop_id))

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_shop_section(self, shop_id: int, shop_section_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', str(shop_id), 'sections', str(shop_section_id))

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_return_policy(self, shop_id: int, return_policy_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', str(shop_id), 'policies', 'return',
                           str(return_policy_id))

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_shipping_profile(self, shop_id: int, shipping_profile_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', str(shop_id), 'shipping-profiles',
                           str(shipping_profile_id))

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_shipping_profiles(self, shop_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', str(shop_id), 'shipping-profiles')

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_production_partners(self, shop_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', str(shop_id), 'production-partners')

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_shop_shipping_profile_upgrades(self, shop_id: int, shipping_profile_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', str(shop_id), 'shipping-profiles',
                           str(shipping_profile_id), 'upgrades')

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_shop_shipping_profile_destinations(self, shop_id: int, shipping_profile_id: int):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', str(shop_id), 'shipping-profiles',
                           str(shipping_profile_id), 'destinations')

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def update_receipt(self, receipt_id: str, body: Dict[str, str]):
        """

        :return:
        """
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', self.store_id, 'receipts', receipt_id)

        response = requests.put(url, headers=self._signed_header, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def create_receipt_shipment(self, receipt_id: str, carrier: str, tracking_code: str, note_to_buyer: str,
                                send_bcc: bool = True):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', self.store_id, 'receipts', receipt_id,
                           'tracking')

        body = {
            "carrier_name": carrier,
            "tracking_code": tracking_code,
            "send_bcc": send_bcc,
            "note_to_buyer": note_to_buyer
        }

        header = self._signed_header
        header['Content-Type'] = 'application/json'

        response = requests.post(url, headers=header, json=body)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def create_shop_section(self, shop_id: str, title: str):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'sections')

        data = {'title': title}

        response = requests.post(url, headers=self._signed_header, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())

    def get_shop_sections(self, shop_id: str):
        url = os.path.join(self.BASE_ETSY_URL, 'application', 'shops', shop_id, 'sections')

        response = requests.get(url, headers=self._signed_header)

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())