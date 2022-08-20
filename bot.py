import json
import os

from dotenv import load_dotenv

from api import create_product, create_flow, fill_fields


def load_menu_to_cms(client_id: str, client_secret: str, menu: list):
    for menu_item in menu:
        print(menu_item['name'])
        print(menu_item['id'])
        create_product(client_id, client_secret, menu_item)


def main():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    with open('menu.json', 'r', encoding='utf-8') as file_menu,\
         open('addresses.json', 'r', encoding='utf-8') as file_addresses:
        menu = json.load(file_menu)
        addresses = json.load(file_addresses)
    #load_menu_to_cms(client_id, client_secret, menu)
    fields = {
        'Address': 'string',
        'Alias': 'string',
        'Longitude': 'float',
        'Latitude': 'float'
    }
    # create_flow(
    #     client_id,
    #     client_secret,
    #     'Pizzeria',
    #     'Information about pizzerias',
    #     fields
    #     )
    # fill_fields(client_id, client_secret, addresses, 'Pizzeria')


if __name__ == '__main__':
    main()
