import argparse
import csv
import os.path

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


def calc_price(prodigi_sku: str, price_sheet_path: str = None):
    if price_sheet_path is None:
        price_sheet_path = os.path.join(PROJECT_DIR, 'prodigi_price_sheets', 'prodigi-prints-photo-art-prints-us.csv')
    with open(price_sheet_path, 'r') as f:
        dict_reader = csv.DictReader(f)
        for row in dict_reader:
            if row['SKU'] == prodigi_sku and row['Shipping method'] == 'Budget':
                total_cost = float(row['Shipping price']) + float(row['Product price'])

                # 25% profit
                selling_price = total_cost * 1.25

                # pass on 6.5% etsy charge to customer
                selling_price *= 1.065

                print(f'${round(selling_price, 2)}')
                break

        print(f'Could not find SKU in {price_sheet_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prodigi_sku', '-s', type=str, required=True, help='SKU listed in Prodigi price sheet')
    parser.add_argument('--price_sheet', type=str, required=False, help='Path to Prodigi price sheet. Default will be'
                                                                        ' used if None')
    args = parser.parse_args()
    calc_price(args.prodigi_sku, args.price_sheet)
