import os
import shutil
from typing import Union, List, Dict
import argparse

from apis.etsy import API as EtsyAPI
from apis.openai import API as OpenaiAPI
import numpy as np
from PIL import Image
import tempfile

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


SHOP_SECTION_TAGS = {
    'BMW E30': ['bmw e30 print', 'bmw 325i', 'bmw e32', 'bmw m3', 'bmw poster', 'bmw wall art', 'm3', 'bmw garage'],
    'Porsche': ['retro porsche', 'porsche 911', '911 turbo', 'vintage porsche'],
    'Corvette': ['corvette', 'corvette art', 'corvette retro'],
    'Jeep': ['Jeep', 'Jeep poster', 'Jeep art', 'Jeep decor', 'Vintage jeep', 'jeep wall art'],
    'BMW E92': ['bmw poster', 'bmw e90', 'bmw e92', 'bmw wall art', 'bmw e92 m3', 'e92', 'bmw_garage'],
    'Motorcycles': ['racing poster', 'motorcycle art', 'isle of man', 'suzuki', 'kawasaki', 'bmw', 'triumph', 'suzuki',
                    'aprilia'],
    'Formula 1': ['formula 1', 'racing', 'drag racing'],
    'Tesla': ['tesla', 'tesla art', 'tesla poster', 'tesla decor']
}

BASE_TAGS = ['boys nursery', 'mens gift', 'boys gift', 'vintage car', 'retro car', 'classic car', 'garage art',
             'car art', 'car enthusiast']

Image.MAX_IMAGE_PIXELS = 278956970

def create_description_chat_message(title: str, product: str) -> List[Dict[str, str]]:
    return [{
        'role': 'user',
        'content': f"Create an Etsy Listing description for a digital product {product} named {title}. Don't include "
                   f"any information about paper weight or dimensions"
    }]


def generate_unique_sku(sku_map: Dict[str, Dict[str, str]]):
    possible_sku = str(np.random.randint(2**63))
    if possible_sku in sku_map.keys():
        return generate_unique_sku(sku_map)
    return possible_sku


def resize_and_compress_image(input_path, output_path, max_size_mb=20):
    # Load the image
    img = Image.open(input_path)

    # Calculate the maximum size in bytes
    max_size_bytes = max_size_mb * 1024 * 1024

    # Get the current image size in bytes
    current_size_bytes = os.path.getsize(input_path)

    # If the image is already smaller than the desired size, no need to resize or compress
    if current_size_bytes <= max_size_bytes:
        img.save(output_path)
        return

    # Calculate the compression quality
    quality = int(100 * max_size_bytes / current_size_bytes)

    # Resize the image while maintaining its aspect ratio
    img.thumbnail((img.width, img.height))

    # Save the resized and compressed image
    img.save(output_path, optimize=True, quality=quality)


def resize_with_max_constraint(input_path, output_path, max_constraint=2000):
    # Load the image
    img = Image.open(input_path)

    # Get the original width and height
    original_width, original_height = img.size

    # Calculate the aspect ratio
    aspect_ratio = original_width / original_height

    # Determine whether the constraint should be applied to width or height
    if original_width >= original_height:
        # Constraint is applied to width
        new_width = min(max_constraint, original_width)
        new_height = int(new_width / aspect_ratio)
    else:
        # Constraint is applied to height
        new_height = min(max_constraint, original_height)
        new_width = int(new_height * aspect_ratio)

    # Resize the image while maintaining aspect ratio
    img = img.resize((new_width, new_height), Image.ANTIALIAS)

    # Save the resized image
    img.save(output_path, ppi=(72, 72))


def create_listing(product_image: str, product_title: str, quantity: Union[int, List[int]], shop_id: int,
                   return_policy_id: int, product: str, shop_section: str):
    etsy_api = EtsyAPI()
    openai_api = OpenaiAPI()

    # These are all required
    listing_data = {
        'title': product_title,
        'should_auto_renew': True,
        'who_made': 'i_did',
        'when_made': '2020_2023',
        'taxonomy_id': '2078',
        'quantity': quantity,
        'price': '4.95',  # Dummy price
        'listing_type': 'digital',
        'shipping_profile_id': 197944947769
    }

    # Resolve shop section ID
    existing_shop_sections_response = etsy_api.get_shop_sections(str(shop_id))
    shop_section_id = None
    for section in existing_shop_sections_response['results']:
        if section['title'].lower() == shop_section.lower():
            shop_section_id = section['shop_section_id']

    if shop_section_id is None:
        create_section_input = input(f"Shop section {shop_section} does not exist. Would you like to create it? (y/n) "
                                     f"\n Existing shop sections: {existing_shop_sections_response['results']}")
        if create_section_input == 'y':
            etsy_api.create_shop_section(shop_id=str(shop_id), title=shop_section)
        else:
            print('Exiting')
            return

    listing_data['shop_section_id'] = shop_section_id

    listing_data['return_policy_id'] = return_policy_id

    description_response = openai_api.chat(create_description_chat_message(title=product_title, product=product))

    listing_data['description'] = description_response['choices'][0]['message']['content']

    tags = SHOP_SECTION_TAGS[shop_section] if shop_section in SHOP_SECTION_TAGS else []
    tags += BASE_TAGS

    listing_data['tags'] = list(set(tags))[:13]

    # Second create the draft listing
    response = etsy_api.create_draft_listing(listing_data, str(shop_id))
    listing_id = response['listing_id']

    # Third upload the listing image and digital image asset

    # Resize the image to the maximum of 20 MB
    asset_tempdir = tempfile.mkdtemp()
    smaller_image_path = os.path.join(asset_tempdir, os.path.basename(product_image))
    resize_and_compress_image(product_image, smaller_image_path)

    file_data = {
        'file': (os.path.basename(product_image), open(smaller_image_path, 'rb'), 'multipart/form-data'),
        'rank': 1
    }

    etsy_api.upload_listing_file(shop_id=str(shop_id), listing_id=str(listing_id), file_data=file_data,
                                 name=os.path.basename(product_image))

    listing_tempdir = tempfile.mkdtemp()
    resized_image_path = os.path.join(listing_tempdir, os.path.basename(product_image))
    resize_with_max_constraint(smaller_image_path, resized_image_path)

    image_data = {
        'image': open(resized_image_path, 'rb'),
        'rank': 1,
        'overwrite': True
    }

    etsy_api.upload_listing_image(shop_id=str(shop_id), listing_id=str(listing_id), image_data=image_data)

    # Finally update the listing fields
    etsy_api.update_listing(shop_id=str(shop_id), listing_id=str(listing_id), listing_data={'is_digital': True,
                                                                                            'type': 'download'})

    shutil.rmtree(asset_tempdir)
    shutil.rmtree(listing_tempdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Required
    parser.add_argument('--product_image', '-p', type=str, required=True,
                        help='Path to the image used for the product that will be used to make the mockups. If '
                             'create_mockups is not flagged and no mockups are provided this will be the only image '
                             'used for the listing')
    parser.add_argument('--title', '-t', type=str, required=True,
                        help='Title of the listing. Will be used to make description by Chat unless description ' \
                             'override is provided')

    # Optionals
    parser.add_argument('--tags', required=False, type=str, help='Tags to be used for listing indexing. Will be '
                                                                 'generated by Chat if not provided based on title')
    parser.add_argument('--quantity', type=str, nargs='+', required=False, default=999,
                        help='The quantity for each dimension. Must supply a number for each variation. Default will be'
                             ' 999 for each variation')
    parser.add_argument('--shop_id', type=int, required=False, default=40548296, help='Etsy shop ID. Defaults to '
                                                                                      'AutoGenerations')
    parser.add_argument('--shop_section', type=str, required=True, help='The shop section ID. If not set then no '
                                                                        'shop section')
    parser.add_argument('--return_policy_id', type=int, required=False, default=1154380155511,
                        help='Return policy ID defines the return policy for the listing. Default is no returns '
                             'accepted')
    parser.add_argument('--product', type=str, required=False, default='poster',
                        help='The product that is going on the listing i.e. poster, sticker sheet, etc. Default is'
                             ' poster')

    args = parser.parse_args()
    create_listing(
        product_image=args.product_image,
        product_title=args.title,
        quantity=args.quantity,
        shop_id=args.shop_id,
        shop_section=args.shop_section,
        return_policy_id=args.return_policy_id,
        product=args.product
    )