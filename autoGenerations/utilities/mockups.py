import os.path
from typing import List, Union

from PIL import Image
from tqdm.auto import tqdm


PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
Image.MAX_IMAGE_PIXELS = 278956970


def create_mockups(input_image_path: str, out_dir: str, dimensions: Union[None, List[str]] = None) -> List[str]:
    """
    Generates mock images for an input product image. Specify the output directory where you would like the files
    written to. This directory will be made if it does not already exist.
    Args:
        input_image_path (str): Path to the product image to create mockups for
        out_dir (str): Path to the directory where the output mock images will be written
        dimensions (list): List of variation dimensions. For now mockup images are scaled in inches only. Default values
            are 8x12, 16x24, 20x30, 24x36
    """
    mockup_images = [
        # Blue wall
        {
            '8x12': {
                'position': (1087, 617),
                'placeholder_dimensions': (322, 489),  # (width, height) in pixels
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'blue_wall_8x12.png')
            },
            '16x24': {
                'position': (923, 371),
                'placeholder_dimensions': (650, 981),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'blue_wall_16x24.png')
            },
            '20x30': {
                'position': (842, 248),
                'placeholder_dimensions': (814, 1228),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'blue_wall_20x30.png')
            },
            '24x36': {
                'position': (757, 122),
                'placeholder_dimensions': (983, 1478),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'blue_wall_24x36.png')
            }
        },

        # Bookshelf
        {
            '8x12': {
                'position': (1160, 541),
                'placeholder_dimensions': (277, 419),  # (width, height) in pixels
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'bookshelf_8x12.png')
            },
            '16x24': {
                'position': (1022, 333),
                'placeholder_dimensions': (555, 838),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'bookshelf_16x24.png')
            },
            '20x30': {
                'position': (950, 223),
                'placeholder_dimensions': (701, 1057),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'bookshelf_20x30.png')
            },
            '24x36': {
                'position': (879, 119),
                'placeholder_dimensions': (840, 1266),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'bookshelf_24x36.png')
            }
        },

        # Table
        {
            '8x12': {
                'position': (810, 681),
                'placeholder_dimensions': (292, 438),  # (width, height) in pixels
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'table_8x12.png')
            },
            '16x24': {
                'position': (659, 458),
                'placeholder_dimensions': (588, 889),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'table_16x24.png')
            },
            '20x30': {
                'position': (586, 349),
                'placeholder_dimensions': (737, 1105),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'table_20x30.png')
            },
            '24x36': {
                'position': (513, 235),
                'placeholder_dimensions': (884, 1331),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'table_24x36.png')
            }
        }
    ]

    dimensions = [
        '8x12',
        '16x24',
        '20x30',
        '24x36'
    ] if dimensions is None else [d.lower() for d in dimensions]

    os.makedirs(out_dir, exist_ok=True)

    product_image = Image.open(input_image_path).convert("RGBA")

    print(f'Generating {len(dimensions)} dimensions each for {len(mockup_images)} mockup images')

    outpaths = []
    for mockup_info in tqdm(mockup_images):
        for dimension in tqdm(dimensions):
            dim = mockup_info[dimension]['placeholder_dimensions']
            resized_image = product_image.resize(dim, Image.LANCZOS)

            mock_image_path = mockup_info[dimension]['path']
            mockup_image = Image.open(mock_image_path)
            top_left = (mockup_info[dimension]['position'][0], mockup_info[dimension]['position'][1])
            mockup_image.paste(resized_image, top_left, mask=resized_image)

            outpath = os.path.join(out_dir, os.path.basename(mock_image_path))
            mockup_image.save(outpath)
            outpaths.append(outpath)

    print(f'Finished writing {len(mockup_images) * len(dimensions)} images to {out_dir}')
    return outpaths
