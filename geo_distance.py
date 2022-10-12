# from geopy import distance
import requests


class CalculateDistanceError(TypeError):
    pass


def calculate_distances(token, addresses):
    delivery_coordinates = fetch_coordinates(
        token,
        addresses
    )
    if delivery_coordinates:
        lon, lat = delivery_coordinates
    return delivery_coordinates


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
