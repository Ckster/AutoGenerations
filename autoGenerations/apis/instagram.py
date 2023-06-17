import os
import requests
from typing import List

import urllib.parse

class API:
    def __init__(self):
        super(API, self).__init__()
        self.BASE_URL = "https://graph.facebook.com/v17.0/"
        self._instagram_user_id = ""  # TODO: Need to get this from secrets file along with token
        self._access_token = ""

    def create_media_container(self, image_url: str, is_carousel_item: bool, caption: str = None):
        url = os.path.join(self.BASE_URL, self._instagram_user_id, 'media')
        url += f'?image_url={image_url}'
        url += f"&is_carousel_item={'true' if is_carousel_item else 'false'}"
        if caption is not None and not is_carousel_item:
            url += f"&caption={caption}"
        url += f'&access_token={self._access_token}'

        response = requests.post(url)

        if response.status_code != 400:
            return response.json()
        else:
            raise LookupError(response.json())

    def create_carousel_container(self, caption: str, children: List[str]):
        url = os.path.join(self.BASE_URL, self._instagram_user_id, 'media')

        url += f"?caption={caption}"

        # Encode children ids
        children = urllib.parse.quote(','.join(children))
        url += f"&children={children}"
        url += f"&media_type=CAROUSEL"
        url += f'&access_token={self._access_token}'

        response = requests.post(url)

        if response.status_code != 400:
            return response.json()
        else:
            raise LookupError(response.json())
