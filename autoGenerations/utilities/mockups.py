import os.path

from PIL import Image


PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


def create_mockups(input_image_path: str, outdir: str):
    mockup_images = [
        # Blue wall
        # {
        #     '8x12': {
        #         'position': (1087, 617),
        #         'placeholder_dimensions': (322, 489),  # (width, height) in pixels
        #         'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'blue_wall_8x12.png')
        #     },
        #     '16x24': {
        #         'position': (923, 371),
        #         'placeholder_dimensions': (650, 981),
        #         'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'blue_wall_16x24.png')
        #     },
        #     '20x30': {
        #         'position': (842, 248),
        #         'placeholder_dimensions': (814, 1228),
        #         'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'blue_wall_20x30.png')
        #     },
        #     '24x36': {
        #         'position': (757, 122),
        #         'placeholder_dimensions': (983, 1478),
        #         'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'blue_wall_24x36.png')
        #     }
        # },

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
                'position': (954, 221),
                'placeholder_dimensions': (701, 1059),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'bookshelf_20x30.png')
            },
            '24x36': {
                'position': (757, 122),
                'placeholder_dimensions': (983, 1478),
                'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'bookshelf_24x36.png')
            }
        },

        # Table
        # {
        #     '8x12': {
        #         'position': (1087, 617),
        #         'placeholder_dimensions': (322, 489),  # (width, height) in pixels
        #         'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'table_8x12.png')
        #     },
        #     '16x24': {
        #         'position': (923, 371),
        #         'placeholder_dimensions': (650, 981),
        #         'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'table_16x24.png')
        #     },
        #     '20x30': {
        #         'position': (842, 248),
        #         'placeholder_dimensions': (814, 1228),
        #         'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'table_20x30.png')
        #     },
        #     '24x36': {
        #         'position': (757, 122),
        #         'placeholder_dimensions': (983, 1478),
        #         'path': os.path.join(PROJECT_DIR, 'data', 'mockup_images', 'table_24x36.png')
        #     }
        # }
    ]

    dimensions = [
    #    '8x12',
    #    '16x24',
        '20x30',
    #    '24x36'
    ]

    product_image = Image.open(input_image_path)

    for mockup_info in mockup_images:
        for dimension in dimensions:
            dim = mockup_info[dimension]['placeholder_dimensions']
            resized_image = product_image.resize(dim, Image.LANCZOS)

            mockup_image = Image.open(mockup_info[dimension]['path'])
            top_left = (mockup_info[dimension]['position'][0], mockup_info[dimension]['position'][1])
            mockup_image.paste(resized_image, top_left, mask=resized_image)
            mockup_image.show()
