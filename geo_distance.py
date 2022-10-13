from geopy import distance
import requests
import re


class CalculateDistanceError(TypeError):
    pass


def calculate_distances(token, addresses, pizzerias_addresses):
    nearest_pizzeria = {'distance': 0, 'address': ''}
    if isinstance(addresses, str):
        delivery_coordinates = fetch_coordinates(
            token,
            addresses
        )
    else:
        delivery_coordinates = addresses
    if not delivery_coordinates:
        raise CalculateDistanceError()
    for pizzeria in pizzerias_addresses:
        pizzeria_coordinates = pizzeria['coordinates']
        pizzeria_distance = re.search(
                r'(.*) km',
                str(
                    distance.distance(
                        pizzeria_coordinates,
                        delivery_coordinates
                    )
                )
        ).group(1)
        if nearest_pizzeria['distance'] == 0:
            nearest_pizzeria['distance'] = pizzeria_distance
        elif float(nearest_pizzeria['distance']) > float(pizzeria_distance):
            nearest_pizzeria['distance'] = pizzeria_distance
            nearest_pizzeria['address'] = pizzeria['address']
    return nearest_pizzeria


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat
