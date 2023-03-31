import os
import json
import requests
from typing import List, Dict
from database.tables import Address, EtsyTransaction, ProdigiRecipient
from database.enums import Prodigi

from datetime import datetime
import openai

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


class Secrets:

    def __init__(self):
        self._secrets_path = os.path.join(PROJECT_DIR, 'openai_secrets.json')
        if not os.path.exists(self._secrets_path):
            raise FileNotFoundError('Could not find openai_secrets.json file in project')

        self._secret_key = None
        with open(self._secrets_path, 'r') as f:
            secrets = json.load(f)
            self._secret_key = secrets['secret_key']

    @property
    def secret_key(self):
        return self._secret_key


class API(Secrets):
    def __init__(self):
        super(API, self).__init__()
        self._signed_header = {
            'Authorization': f"Bearer {self._secret_key}"
        }

    def chat(self, messages: List[Dict[str, str]], model: str = 'gpt-3.5-turbo'):
        url = os.path.join("https://api.openai.com/v1/", 'chat', 'completions')

        data = {
            'model': model,
            'messages': messages
        }

        header = self._signed_header
        header['Content-Type'] = 'application/json'

        print(json.dumps(data))

        response = requests.post(url, headers=self._signed_header, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()
        else:
            raise LookupError(response.json())
