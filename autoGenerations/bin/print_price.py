from typing import Union
import argparse
import csv
import os.path
import math

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


def calc_price(prodigi_sku: str, price_sheet_path: str = None) -> Union[str, None]:
    if price_sheet_path is not None:
        price_sheet_paths = [price_sheet_path]
    else:
        price_sheet_paths = [
            os.path.join(PROJECT_DIR, 'prodigi_price_sheets', 'prodigi-prints-photo-art-prints-us.csv'),
            os.path.join(PROJECT_DIR, 'prodigi_price_sheets', 'prodigi-prints-fine-art-prints-us.csv')
        ]

    for price_sheet_path in price_sheet_paths:
        with open(price_sheet_path, 'r') as f:
            dict_reader = csv.DictReader(f)
            for row in dict_reader:
                if row['SKU'] == prodigi_sku and row['Shipping method'] == 'Budget':
                    # Can only have one shipping profile per variation so fix shipping cost to $10 and pass on
                    # difference
                    shipping_price = float(row['Shipping price'])
                    pass_on = shipping_price - 9.95

                    product_price = float(row['Product price'])
                    total_cost =  product_price + shipping_price

                    # 30% profit
                    selling_price = product_price * 1.40 + pass_on

                    # pass on 6.5% etsy charge to customer
                    selling_price *= 1.065

                    selling_price = math.ceil(selling_price) - 0.05

                    print(f'Selling price: {selling_price}, shipping price: {9.95},'
                          f' profit {selling_price + 9.95 - total_cost}')
                    return str(selling_price)

    print(f'Could not find SKU in {price_sheet_path}')
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prodigi_sku', '-s', type=str, required=True, help='SKU listed in Prodigi price sheet')
    parser.add_argument('--price_sheet', type=str, required=False, help='Path to Prodigi price sheet. Default will be'
                                                                        ' used if None')
    args = parser.parse_args()
    calc_price(args.prodigi_sku, args.price_sheet)
