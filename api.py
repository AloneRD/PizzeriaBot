import requests
import os
from datetime import datetime


def get_access_token(client_id: str, client_secret: str) -> str:
    response_token_request = requests.post(
        'https://api.moltin.com/oauth/access_token',
        data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
            }
        )
    response_token_request.raise_for_status()
    access_token = response_token_request.json()
    os.environ.setdefault(
        'MOLTIN_TOKEN_EXPIRES_TIME',
        str(access_token['expires'])
        )
    os.environ.setdefault('ACCESS_TOKEN', access_token['access_token'])


def check_access_token(client_id: str, client_secret: str):
    token_expires_time = os.getenv('MOLTIN_TOKEN_EXPIRES_TIME')
    timestamp = int(datetime.now().timestamp())
    if not token_expires_time or int(token_expires_time) < timestamp:
        get_access_token(client_id, client_secret)


def create_product(client_id: str, client_secret: str, product: dict):
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    product_img = product['product_image']

    headers = {'Authorization': access_token}
    json_data = {
        'data': {
            'type': 'product',
            'name': product['name'],
            'slug': str(product['id']),
            'sku': f"{product['name']}_{product['id']}",
            'description': product['description'],
            'manage_stock': True,
            'price': [
                {
                    'amount':  product['price'],
                    'currency': 'RUB',
                    'includes_tax': True,
                },
            ],
            'status': 'live',
            'commodity_type': 'physical',
        },
    }
    response_create_product = requests.post(
        'https://api.moltin.com/v2/products',
        headers=headers,
        json=json_data
        )
    response_create_product.raise_for_status()
    product_id = response_create_product.json()['data']['id']
    img_id = create_file(client_id, client_secret, product_img)
    link_image_to_product(client_id, client_secret, product_id, img_id)


def create_file(client_id: str, client_secret: str, file: str) -> str:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')

    file_url = file['url']

    headers = {'Authorization': access_token}
    files = {
        'file_location': (None, file_url),
        }

    response_create_file = requests.post(
        'https://api.moltin.com/v2/files',
        headers=headers,
        files=files
        )
    response_create_file.raise_for_status()
    img_id = response_create_file.json()['data']['id']
    return img_id


def link_image_to_product(client_id: str, client_secret: str, product_id: str, img_id: str):
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')

    headers = {'Authorization': access_token}
    json_data = {
        'data': {
            'type': 'main_image',
            'id': img_id,
        },
    }
    response_relationship = requests.post(
        f'https://api.moltin.com/v2/products/{product_id}/relationships/main-image',
        headers=headers,
        json=json_data
        )
    response_relationship.raise_for_status()


def create_flow(client_id: str, client_secret: str, name: str, description: str, fields: dict):
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    json_data = {
        'data': {
            'type': 'flow',
            'name': name,
            'slug': name,
            'description': description,
            'enabled': True,
        },
    }

    response_create_flow = requests.post(
        'https://api.moltin.com/v2/flows',
        headers=headers,
        json=json_data
        )
    response_create_flow.raise_for_status()
    flow = response_create_flow.json()['data']
    create_fields(client_id, client_secret, fields, flow)


def create_fields(client_id: str, client_secret: str, fields: dict, flow: str):
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    for field_name, field_type in fields.items():
        json_data = {
            'data': {
                'type': 'field',
                'name': field_name,
                'slug': field_name,
                'field_type': field_type,
                'description': field_name,
                'required': False,
                'enabled': False,
                'relationships': {
                    'flow': {
                        'data': {
                            'id': flow['id'],
                            'type': 'flow'
                        }
                    }
                }
            }
        }
        response_create_field = requests.post(
            'https://api.moltin.com/v2/fields',
            headers=headers,
            json=json_data
            )
        response_create_field.raise_for_status()


def fill_fields(client_id: str, client_secret: str, data_items: list, flow_slug: str):
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    for data_item in data_items:
        json_data = {
            'data': {
                'type': 'entry',
                'Address': data_item['address']['full'],
                'Alias': data_item['alias'],
                'Longitude': float(data_item['coordinates']['lon']),
                'Latitude': float(data_item['coordinates']['lat'])
            }
        }
        response_field_fill = requests.post(
            f'https://api.moltin.com/v2/flows/{flow_slug}/entries',
            headers=headers,
            json=json_data
            )
        response_field_fill.raise_for_status()


def get_products(client_id: str, client_secret: str) -> dict:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_products = requests.get(
        'https://api.moltin.com/v2/products',
        headers=headers
        )
    response_products.raise_for_status()
    return response_products.json()


def get_product(client_id: str, client_secret: str, id: str) -> dict:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_products = requests.get(
        f'https://api.moltin.com/v2/products/{id}',
        headers=headers
        )
    response_products.raise_for_status()
    return response_products.json()


def get_image_product(client_id: str, client_secret: str, id_image: str) -> dict:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_products = requests.get(
        f'https://api.moltin.com/v2/files/{id_image}',
        headers=headers
        )
    response_products.raise_for_status()
    return response_products.json()


def add_product_cart(product: dict, client_id: str, client_secret: str, quantity: int, cart_id: str) -> None:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    json_data = {
        'data': {
            'id': product['id'],
            'type': 'cart_item',
            'quantity': quantity,
        },
    }
    response_add_product_to_cart = requests.post(
        f'https://api.moltin.com/v2/carts/{cart_id}_pizzeria/items',
        headers=headers,
        json=json_data
        )
    response_add_product_to_cart.raise_for_status()


def remove_product_from_cart(cart_id: str, product_id: str, client_id: str, client_secret:str) -> None:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_add_product_to_cart = requests.delete(
        f'https://api.moltin.com/v2/carts/{cart_id}_pizzeria/items/{product_id}',
        headers=headers,
        )
    response_add_product_to_cart.raise_for_status()


def get_cart(cart_id: str, client_id: str, client_secret: str) -> dict:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_get_cart = requests.get(
        f'https://api.moltin.com/v2/carts/{cart_id}_pizzeria/items',
        headers=headers
        )
    response_get_cart.raise_for_status()
    return response_get_cart.json()


def remove_cart(cart_id: str, client_id: str, client_secret: str):
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_remove_cart = requests.delete(
        f'https://api.moltin.com/v2/carts/{cart_id}_pizzeria/items',
        headers=headers
        )
    response_remove_cart.raise_for_status()


def get_cart_total(cart_id: str, client_id: str, client_secret: str) -> str:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_get_cart = requests.get(
        f'https://api.moltin.com/v2/carts/{cart_id}_pizzeria',
        headers=headers
        )
    response_get_cart.raise_for_status()
    cart = response_get_cart.json()
    total_cart = cart['data']['meta']['display_price']['with_tax']['formatted']
    return total_cart


def create_customer(name: str, email: str, client_id: str, client_secret:str) -> None:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    json_data = {
        'data': {
            'type': 'customer',
            'name': name,
            'email': email,
        },
    }
    response_create_customer = requests.post(
        'https://api.moltin.com/v2/customers',
        headers=headers,
        json=json_data
        )
    response_create_customer.raise_for_status()


def get_pizzerias(slug: str, client_id: str, client_secret: str) -> list:
    check_access_token(client_id, client_secret)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {'Authorization': access_token}
    response_get_cart = requests.get(
        f'https://api.moltin.com/v2/flows/{slug}/entries',
        headers=headers
        )
    response_get_cart.raise_for_status()
    pizzerias = response_get_cart.json()['data']
    return pizzerias