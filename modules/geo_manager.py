import mgrs
import functools
import requests

api_key = 'AIzaSyBhg2-Xkv5u9elauvCJWPih6TK_1g0zLgM'

@functools.lru_cache()
def _get_mgrs_from_lat_lng(lat, lng):
    return mgrs.MGRS().toMGRS(lat, lng)


@functools.lru_cache()
def _get_mgrs_level(mgrs, level):
    mgrs_4 = mgrs[:-10]
    if level in [6, 8, 10, 12]:
        index = int((level-4)/2)
        return mgrs_4 + mgrs[-10:][:5][:index] + mgrs[-10:][5:][:index]
    if level == 4:
        return mgrs_4
    mgrs_2 = mgrs[:-12]
    if level == 2:
        return mgrs_2


def _get_mgrs_with_level_from_lat_lng(lat, lng, level=8):
    return _get_mgrs_level(_get_mgrs_from_lat_lng(lat, lng), level)


def _get_mgrs_area(lat, lng, mgrs_level):

    accuracy = {2: 0.007, 4: 0.0007, 6: 0.00007, 8: 0.000007,
                     10: 0.0000007, 12: 0.00000007}[mgrs_level]
    accuracy = {2: 0.01, 4: 0.001, 6: 0.0001, 8: 0.00001,
                10: 0.000001, 12: 0.0000001}[mgrs_level]
                
    return {_get_mgrs_with_level_from_lat_lng(lat, lng, mgrs_level),
            _get_mgrs_with_level_from_lat_lng(
                lat + accuracy, lng, mgrs_level),
            _get_mgrs_with_level_from_lat_lng(
                lat, lng + accuracy, mgrs_level),
            _get_mgrs_with_level_from_lat_lng(
                lat + accuracy, lng + accuracy, mgrs_level),
            _get_mgrs_with_level_from_lat_lng(
                lat, lng, mgrs_level),
            _get_mgrs_with_level_from_lat_lng(
                lat - accuracy, lng, mgrs_level),
            _get_mgrs_with_level_from_lat_lng(
                lat, lng - accuracy, mgrs_level),
            _get_mgrs_with_level_from_lat_lng(
                lat - accuracy, lng - accuracy, mgrs_level),
            _get_mgrs_with_level_from_lat_lng(
                lat + accuracy, lng - accuracy, mgrs_level),
            _get_mgrs_with_level_from_lat_lng(lat - accuracy, lng + accuracy, mgrs_level)}


def get_nearest_top_almarcat_city(lat, lng, top='100'):
    response = requests.get('https://www.almarcat.com/_api/v1/City/Nearest/{lat}/{lng}/{top}'.format(lat=lat, lng=lng, top=top)).json()
    return response

def _get_lat_lng_from_adress(adress):
    resp_json_payload = _get_geocoding(adress)
    if len(resp_json_payload['results']) == 0:
        return {'lat':None, 'lng':None}
    return resp_json_payload['results'][0]['geometry']['location']


def _get_geocoding(adress):
    language = 'es'
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?address={}&language={}&key={}'.format(adress, language, api_key))
    return response.json()

@functools.lru_cache()
def _get_reverse_geocoding(lat, lng):
    language = 'es'
    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&language={}&key={}'.format(lat, lng, language, api_key))
    return response.json()

def get_long_locality_from_geocode(geocode):
    for reslut in geocode['results']:
        address_components = reslut['address_components']
        for component in address_components:
            if 'locality' in component['types']:
                return component['long_name']

def get_long_administrative_area_level_2_from_geocode(geocode):
    for reslut in geocode['results']:
        address_components = reslut['address_components']
        for component in address_components:
            if 'administrative_area_level_2' in component['types']:
                return component['long_name']

def get_long_administrative_area_level_1_from_geocode(geocode):
    for reslut in geocode['results']:
        address_components = reslut['address_components']
        for component in address_components:
            if 'administrative_area_level_1' in component['types']:
                return component['long_name']

def get_short_country_from_geocode(geocode):
    for reslut in geocode['results']:
        address_components = reslut['address_components']
        for component in address_components:
            if 'country' in component['types']:
                return component['short_name']

def get_short_administrative_area_level_2_from_geocode(geocode):
    for reslut in geocode['results']:
        address_components = reslut['address_components']
        for component in address_components:
            if 'administrative_area_level_2' in component['types']:
                return component['short_name']

def get_country_from_geocode(geocode):
    for reslut in geocode['results']:
        address_components = reslut['address_components']
        for component in address_components:
            if 'country' in component['types']:
                return component['short_name']

# accuracy = {2: 0.01, 4: 0.001, 6: 0.0001, 8: 0.00001,
#             10: 0.000001, 12: 0.0000001}[mgrs_level]
