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
from utilities.mockups import create_mockups as generate_mockups

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))

PROPERTY_ID_LOOKUP = {
    501: 'Dimensions',
    507: 'Material'
}


# Shop section IDs
# Porsche: 41699988
# BMW E30: 41695359

# TODO: Taxonomy ID
# TODO: Return Policy ID

def create_description_chat_message(title: str, product: str) -> List[Dict[str, str]]:
    return [{
        'role': 'user',
        'content': f"Create an Etsy Listing description for a {product} named {title}. Don't include any "
                   f"information about paper weight or dimensions"
    }]


def create_tags_chat_message(title: str, product: str) -> List[Dict[str, str]]:
    return [{
        'role': 'user',
        'content': f"Create an Etsy Listing indexing tag list with 13 tags for a {product} named {title} in Python"
                   f" list format. Each tag cannot exceed 20 characters in length. Only use standard alphabet"
                   f" characters."
    }]


def create_listing(product_image: str, product_title: str, create_mockups: bool, prodigi_sku: str,
                   dimensions: Union[str, List[str]], quantity: Union[int, List[int]], shop_id: int,
                   listing_type: str, shipping_profile_id: int, property_id: int, scale_id: int,
                   mockups: Union[List[str], None], product: str, shop_section: str):
    etsy_api = EtsyAPI()
    openai_api = OpenaiAPI()
    gc_storage = Storage()

    has_variations = isinstance(dimensions, list)
    if not has_variations:
        dimensions = [dimensions]

    # These are all required
    listing_data = {
        'title': product_title,
        'has_variations': has_variations,
        'should_auto_renew': True,
        'who_made': 'i_did',
        'when_made': 'made_to_order',
        'taxonomy_id': '2078',
        'quantity': '999' if has_variations else quantity,
        'price': '100',  # Dummy price
        'listing_type': listing_type
    }

    # Resolve shop section ID
    existing_shop_sections_response = etsy_api.get_shop_sections(str(shop_id))
    shop_section_id = None
    for section in existing_shop_sections_response['results']:
        if section['title'].lower() == shop_section.lower():
            shop_section_id = section['shop_section_id']

    if shop_section_id is None:
        create_section_input = input(f'Shop section {shop_section} does not exist. Would you like to create it? (y/n)')
        if create_section_input == 'y':
            etsy_api.create_shop_section(shop_id=str(shop_id), title=product_title)
        else:
            print('Exiting')
            return

    listing_data['shop_section_id'] = shop_section_id

    # Need to resolve a shipping profile ID for physical items
    if listing_type == 'physical':
        listing_data['shipping_profile_id'] = shipping_profile_id

    inventory_information = {
        'products': [],
        'price_on_property': [property_id],
        'quantity_on_property': [property_id],
        'sku_on_property': [property_id]
    }

    skus = []
    for i, dimension in enumerate(dimensions):
        dim_prodigi_sku = prodigi_sku + dimension
        dim_etsy_sku = (product_title.replace(' ', '_').upper() + '_' + dimension).upper()[:32]

        dim_price = calc_price(dim_prodigi_sku)
        if dim_price is None:
            raise LookupError(f'Could not find price for {dim_prodigi_sku}')

        dim_quantity = quantity[i] if isinstance(quantity, list) else quantity
        skus.append({'etsy': dim_etsy_sku, 'prodigi': dim_prodigi_sku})

        inventory_information['products'].append(
            {
                'sku': dim_etsy_sku,
                'property_values': [
                    {
                        'property_id': property_id,
                        'value_ids': [i + 1],
                        'scale_id': scale_id,
                        'property_name': PROPERTY_ID_LOOKUP[property_id] if property_id in PROPERTY_ID_LOOKUP else None,
                        'values': [dimension]
                    }
                ],
                'offerings': [
                    {
                        'price': dim_price,
                        'quantity': dim_quantity,
                        'is_enabled': True
                    }
                ]
            }
        )

    description_response = openai_api.chat(create_description_chat_message(title=product_title, product=product))
    tags_response = openai_api.chat(create_tags_chat_message(title=product_title, product=product))

    listing_data['description'] = description_response['choices'][0]['message']['content']

    tags = tags_response['choices'][0]['message']['content'].replace('[', '').replace(']', '').split(',')
    tags = [t for t in tags if len(t) < 20][:13]
    print(tags)

    listing_data['tags'] = tags

    print(skus)

    # First upload the product image to google cloud storage
    cloud_storage_path = os.path.join(shop_section, os.path.basename(product_image))
    gc_storage.upload_image(image_path=product_image, cloud_storage_path=cloud_storage_path)

    # Second create the draft listing
    response = etsy_api.create_draft_listing(listing_data, str(shop_id))
    listing_id = response['listing_id']

    # Third add the product inventory (variations)
    etsy_api.update_listing_inventory(str(listing_id), inventory_information)

    # Fourth upload the product images
    tempdir = None
    if mockups is not None:
        mockup_images = mockups

    elif create_mockups:
        print('Creating mockup images')
        tempdir = tempfile.mkdtemp(prefix='mockups')
        mockup_images = generate_mockups(product_image, tempdir, dimensions=dimensions)
        try:
            mockup_images = sorted(mockup_images, key=lambda x: int(x.lower().split('_')[-1].split('x')[0]),
                                   reverse=True)
        except Exception as e:
            print('Tried sorting mockups so largest size was thumbnail but it failed, check this manually')

    else:
        mockup_images = [product_image]

    for i, mock_image in enumerate(mockup_images):
        # Can only have 10 images in listing
        if i > 9:
            continue

        image_data = {
            'image': open(mock_image, 'rb'),
            'rank': i + 1,
            'overwrite': True
        }
        etsy_api.upload_listing_image(shop_id=str(shop_id), listing_id=str(listing_id), image_data=image_data)

    if tempdir is not None:
        shutil.rmtree(tempdir)

    # Finally update the SKU map with the new listing info
    with open(os.path.join(PROJECT_DIR, 'sku_map.json'), 'r') as f:
        sku_map = json.load(f)

    for sku in skus:
        sku_map[sku['etsy']] = {
            'prodigi_sku': sku['prodigi'],
            'asset_url': cloud_storage_path
        }

    with open(os.path.join(PROJECT_DIR, 'sku_map.json'), 'w') as f:
        json.dump(sku_map, f, indent=1)

    print('Added listing and updated sku map')


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
    parser.add_argument('--create_mockups', '-m', action='store_true',
                        help='If set then mockups are made. Not all product types support auto mocking')

    # Optionals
    parser.add_argument('--prodigi_sku', '-sku',
                        type=str, help='Base Prodigi SKU to be used in conjunction with dimensions.'
                                       ' Default is EP-GLOBAL-PAP-', required=False, default='EP-GLOBAL-PAP-')
    parser.add_argument('--dimensions', '-d', type=str, nargs='+', required=False,
                        default=['8X12', '16X24', '20X30', '24X36'],
                        help='Dimension(s) to be offered for the product. If multiple dimensions separate the values'
                             ' with a comma like 8X12,16X24')

    parser.add_argument('--description', required=False, type=str, help='Description to be used for the listing. Will'
                                                                        'be generated by Chat based on listing title if'
                                                                        ' not provided')
    parser.add_argument('--tags', required=False, type=str, help='Tags to be used for listing indexing. Will be '
                                                                 'generated by Chat if not provided based on title')
    parser.add_argument('--mockups', type=str, nargs='+', required=False, help='Path(s) to mockup file(s). Will '
                                                                               'override create_mockups flag if ' \
                                                                               'provided ')
    parser.add_argument('--quantity', type=str, nargs='+', required=False, default=999,
                        help='The quantity for each dimension. Must supply a number for each variation. Default will be'
                             ' 999 for each variation')
    parser.add_argument('--shop_id', type=int, required=False, default=40548296, help='Etsy shop ID. Defaults to '
                                                                                      'AutoGenerations')
    parser.add_argument('--shop_section', type=str, required=True, help='The shop section ID. If not set then no '
                                                                        'shop section')
    parser.add_argument('--listing_type', type=str, required=False, default='physical',
                        help='Whether the listing is a physical or digital product. Default is physical.')
    parser.add_argument('--shipping_profile_id', type=int, required=False, default=197559363961,
                        help='Shipping profile ID defines the shipping time, price, etc. Default is free shipping'
                             ' processing in 5-7 business days')
    parser.add_argument('--property_id', type=int, required=False, default=501,
                        help='Defines the type of property to create product variations on. The id is defined by Etsy.'
                             'The default is 501 which is variation by Dimension')
    parser.add_argument('--scale_id', type=int, required=False, default=344,
                        help='Defines the scale (unit) of the property used to create variations. The id is defined by'
                             ' Etsy.The default is 344 which is inches')
    parser.add_argument('--product', type=str, required=False, default='poster',
                        help='The product that is going on the listing i.e. poster, sticker sheet, etc. Default is'
                             ' poster')

    args = parser.parse_args()
    create_listing(
        product_image=args.product_image,
        product_title=args.title,
        create_mockups=args.create_mockups,
        prodigi_sku=args.prodigi_sku,
        dimensions=args.dimensions,
        quantity=args.quantity,
        shop_id=args.shop_id,
        shop_section=args.shop_section,
        listing_type=args.listing_type,
        shipping_profile_id=args.shipping_profile_id,
        property_id=args.property_id,
        scale_id=args.scale_id,
        mockups=args.mockups,
        product=args.product
    )
