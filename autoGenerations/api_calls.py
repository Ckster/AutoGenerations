import os
import json
import requests

PROJECT_DIR = os.path.dirname(__file__)


class Secrets:

    def __init__(self):
        self._secrets_path = os.path.join(PROJECT_DIR, 'secrets.json')
        if not os.path.exists(self._secrets_path):
            raise FileNotFoundError('Could not find secrets.json file in project')

        self._store_id = None
        self._shared_secret = None
        self._keystring = None
        with open(self._secrets_path, 'r') as f:
            secrets = json.load(f)
            self._store_id = secrets['store_id']
            self._shared_secret = secrets['shared_secret']
            self._keystring = secrets['keystring']

    @property
    def keystring(self):
        return self._keystring

    @property
    def shared_secret(self):
        return self._shared_secret

    @property
    def store_id(self):
        return self._store_id


class API(Secrets):
    BASE_URL = 'https://api.etsy.com/v3'

    def __init__(self):
        super(API, self).__init__()

    def get_receipts(self):
        url = os.path.join(self.BASE_URL, 'application', 'shops', self.store_id, 'receipts')

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "x-api-key": self.keystring,
            "Authorization": "Bearer 695701628.XNNGfvXB_MCsSboo1APl9qYzan0ntPsQLmUt6a3gRu_d1wrk3PTrYVZFDgHeVwhTu-FV145J0ZOy3nAnMHkLhk3X2c"
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
