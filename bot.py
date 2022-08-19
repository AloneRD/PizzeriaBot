import json
import os

from dotenv import load_dotenv

from api import create_product


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


if __name__ == '__main__':
    main()
