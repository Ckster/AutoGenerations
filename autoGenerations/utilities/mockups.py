import os.path
from typing import List, Union

from PIL import Image
from tqdm.auto import tqdm
from PIL import Image, ImageDraw, ImageFont
import numpy as np


PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
Image.MAX_IMAGE_PIXELS = 278956970

IMAGE_POSITIONS = {
    'simple_2:3': [
        {
            'mockup': {
                'position': (953, 397),
                'placeholder_dimensions': (1021-953, 2006-397),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'simplistic_mockup_2:3.png')
            }
        },
        {
            'top_right': {
                'zoom': 1,
                'position_ratios': (5/6, 1/6),
                'path': 'top_right.png'
            }
        },
        {
            'bottom_left': {
                'zoom': 1,
                'position_ratios': (1/6, 5/6),
                'path': 'bottom_left.png'
            }
        }
    ],
    'simple_3:2': [
        {
            'mockup': {
                'position': (620, 608),
                'placeholder_dimensions': (2384 - 620, 1785 - 608),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'simplistic_mockup_3:2.png')
            }
        },
        {
            'top_right': {
                'zoom': 1,
                'position_ratios': (5/6, 1/6),
                'path': 'top_right.png'
            }
        },
        {
            'bottom_left': {
                'zoom': 1,
                'position_ratios': (1/6, 5/6),
                'path': 'bottom_left.png'
            }
        }
    ],
    'apartment': [
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
}


def zoom_at(img, x, y, zoom):
    w, h = img.size
    zoom2 = zoom * 2
    img = img.crop((max(0, x - w / zoom2), max(0, y - h / zoom2),
                    min(w, x + w / zoom2), min(h, y + h / zoom2)))
    return img.resize((w, h), Image.LANCZOS)


def add_watermark(input_image_path, output_image_path, watermark_text):
    # Open the input image
    image = Image.open(input_image_path)
    # Create a transparent layer for the watermark
    watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
    # Choose a font and font size for the watermark
    font = ImageFont.truetype(os.path.join(PROJECT_DIR, 'data', 'fonts', "Nunito-Italic-VariableFont_wght.ttf"), 30)
    # Calculate the position to place the watermark (centered)
    for x_ratio in np.linspace(0, 1.1, 10):
        for y_ratio in np.linspace(0, 2, 20):
            x = int(image.width * x_ratio)
            y = int(image.height * y_ratio)
            draw = ImageDraw.Draw(watermark)
            draw.text((0, 0), watermark_text, font=font, fill=(255, 255, 255, 80))
            rotated_watermark = watermark.rotate(45, expand=True)
            image.paste(rotated_watermark, (x, y - image.width), mask=rotated_watermark)
    # Save the watermarked image
    image.save(output_image_path)
    
def add_copyright(input_image_path, copyright_text: str):
    input_image = Image.open(input_image_path)
    copyright = Image.new("RGBA", input_image.size, (0, 0, 0, 0))
    font = ImageFont.truetype(os.path.join(PROJECT_DIR, 'data', 'fonts', 'IBMPlexMono-Bold.ttf'), 50)
    draw = ImageDraw.Draw(copyright)
    draw.text((0, 0), copyright_text, font=font, fill=(0, 0, 0, 255))
    text_width, text_height = draw.textsize(copyright_text, font)
    input_image.paste(copyright, ((input_image.width - text_width) // 2, int(input_image.height * 0.95)),
                      mask=copyright)
    input_image.save(input_image_path)


def create_mockup(mockup_info, dimension: str, product_image: Image, out_dir: str) -> str:
    dim = mockup_info[dimension]['placeholder_dimensions']
    resized_image = product_image.resize(dim, Image.LANCZOS)

    mock_image_path = mockup_info[dimension]['path']
    mockup_image = Image.open(mock_image_path)
    top_left = (mockup_info[dimension]['position'][0], mockup_info[dimension]['position'][1])
    mockup_image.paste(resized_image, top_left, mask=resized_image)

    outpath = os.path.join(out_dir, os.path.basename(mock_image_path))
    mockup_image.save(outpath)
    return outpath


def create_zoomed_image(mockup_info, image_type: str, product_image: Image, out_dir: str) -> str:
    w = product_image.size[0]
    h = product_image.size[1]
    ratios = mockup_info[image_type]['position_ratios']
    zoom = mockup_info[image_type]['zoom']
    zoomed_image = zoom_at(product_image, int(w * ratios[0]), int(h * ratios[1]), zoom)
    nw = 2000 if w < h else int(2000 * (w/h))
    nh = 2000 if h < w else int(2000 * (h/w))
    print(f'resizing to {(nw, nh)}')
    zoomed_image = zoomed_image.resize((nw, nh))

    mock_image_path = mockup_info[image_type]['path']
    outpath = os.path.join(out_dir, os.path.basename(mock_image_path))

    zoomed_image.save(outpath, ppi=(72, 72))
    return outpath

def create_listing_images(input_image_path: str, out_dir: str, style: str = 'simple_2:3') -> List[str]:
    """
    Generates mock images for an input product image. Specify the output directory where you would like the files
    written to. This directory will be made if it does not already exist.
    Args:
        input_image_path (str): Path to the product image to create mockups for
        out_dir (str): Path to the directory where the output mock images will be written
    """
    os.makedirs(out_dir, exist_ok=True)

    product_image = Image.open(input_image_path).convert("RGBA")

    mockup_images = IMAGE_POSITIONS[style]

    outpaths = []
    for mockup_info in tqdm(mockup_images):
        images = list(mockup_info.keys())
        for image in tqdm(images):
            image_info = list(mockup_info[image].keys())
            if 'placeholder_dimensions' in image_info:
                outpath = create_mockup(mockup_info, image, product_image, out_dir)
            elif 'zoom' in image_info:
                outpath = create_zoomed_image(mockup_info, image, product_image, out_dir)
            else:
                continue

            add_watermark(outpath, outpath, 'AutoGenerations')
            add_copyright(outpath, '\u00A9 2023 AutoGenerations')
            outpaths.append(outpath)

    print(f'Finished writing images to {out_dir}')
    return outpaths
