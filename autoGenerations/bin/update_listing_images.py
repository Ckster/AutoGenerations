import json
import os
import shutil
from typing import Union, List, Dict
import argparse
import tempfile

from apis.etsy import API as EtsyAPI
from apis.openai import API as OpenaiAPI
from apis.google_cloud import Storage
from bin.print_price import calc_price
from utilities.mockups import create_listing_images
import numpy as np
import urllib

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


def update_listing_images(listing_id: str, product_image_path: str, aspect_ratio: str, shop_id: str,
                          new_image_dir: str):
    etsy_api = EtsyAPI()

    if new_image_dir is None:
        tempdir = tempfile.mkdtemp(prefix='mockups')
        mockup_images = create_listing_images(product_image_path, tempdir, style=f'simple_{aspect_ratio}')
        mockup_images.reverse()
    else:
        mockup_images = [os.path.join(new_image_dir, file) for file in os.listdir(new_image_dir)]

    existing_images_response = etsy_api.get_listing_images(shop_id, listing_id)

    for image in existing_images_response['results']:
        image_id = image['listing_image_id']
        etsy_api.delete_listing_image(shop_id, listing_id, image_id)

    for i, mock_image in enumerate(mockup_images):
        # Can only have 10 images in listing
        if i > 9:
            continue

        image_data = {
            'image': open(mock_image, 'rb'),
            'rank': i + 1,
            'overwrite': True
        }
        response = etsy_api.upload_listing_image(shop_id=str(shop_id), listing_id=str(listing_id),
                                                 image_data=image_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--listing_id', type=str, required=True, help='ID of the listing to update the images for')
    parser.add_argument('--product_image', type=str, required=True, help='Path to the image to use for the product')
    parser.add_argument('--aspect_ratio', type=str, required=True, help='Aspect ratio of the new mockup images, 2:3, '
                                                                        '3:2 etc')

    parser.add_argument('--shop_id', type=str, required=False, default='40548296', help='Etsy shop ID. Defaults to '
                                                                                      'AutoGenerations')
    parser.add_argument('--new_image_dir', type=str, required=False, help='Path to new images to use instead of '
                                                                          'generating new mockups')
    args = parser.parse_args()
    update_listing_images(args.listing_id, args.product_image, args.aspect_ratio, args.shop_id, args.new_image_dir)
