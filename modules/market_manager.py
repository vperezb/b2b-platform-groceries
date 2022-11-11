import functools

from modules import utils, geo_manager, store_manager, item_manager

avaliable_countries = ['ES']

avaliable_aal1s = ['Ceuta', 'Melilla']

avaliable_aal2s = ['Barcelona', 'Tarragona', 'Madrid', 'Valencia', 'Asturias', 'Alicante',
 'Lleida', 'Toledo', 'Girona', 'Valladolid', 'León', 'Teruel', 'La Rioja', 'Córdoba', 'Cáceres',
 'Zaragoza', 'A Coruña', 'Sevilla', 'Gipuzkoa', 'Pontevedra', 'Ávila', 'Badajoz', 'Zamora',
 'Ourense', 'Palencia', 'Huesca', 'Salamanca', 'Jaén', 'Navarra', 'Albacete', 'Lugo', 'Cádiz',
 'Cuenca', 'Ciudad Real', 'Granada', 'Guadalajara', 'Burgos', 'Cantabria', 'Castelló', 'Murcia',
 'Illes Balears', 'Segovia', 'Málaga', 'Vizcaya', 'Soria', 'Castellón', 'Bizkaia', 'La Coruña',
 'Álava', 'Araba', 'Biscay', 'Navarre', 'Province of Ourense',
 'Las Palmas']

avaliable_localities = ['Terrassa', 'Barcelona', 'Mataró', 'Vilanova i la Geltrú',
 'Rubí', 'Valls', 'Sabadell', 'Malgrat de Mar', 'Cerdanyola del Vallès', 'Salou',
 'Sant Boi de Llobregat', 'Santa Coloma de Gramenet', 'Ripollet', 'Manlleu',
 'Tona', 'Premià de Mar', 'Castellar del Vallès', "Sant Sadurní d'Anoia", 'Sitges', 'Tordera',
 'Gavà']


def get_pal_from_geocode(geocode):
    locality = geo_manager.get_long_locality_from_geocode(geocode)
    long_administrative_area_level_2 = geo_manager.get_long_administrative_area_level_2_from_geocode(geocode)
    long_administrative_area_level_1 = geo_manager.get_long_administrative_area_level_1_from_geocode(geocode)
    country = geo_manager.get_country_from_geocode(geocode)

    return {
        'locality': locality,
        'aal2': long_administrative_area_level_2,
        'aal1': long_administrative_area_level_1,
        'country': country
    }

def assign_market_from_pal(country, aal1, aal2, locality):
    if country and country in avaliable_countries:
        if locality and locality in (avaliable_localities):
            return ({
                'type': 'locality',
                'locality': locality,
                'aal2': aal2,
                'aal1': aal1,
                'country': country
            }) # Returns locality the country and aa1 --> Premià de Mar
        elif aal2 and aal2 in avaliable_aal2s:
            return ({
                'type': 'aal2',
                'locality': locality,
                'aal2': aal2,
                'aal1': aal1,
                'country': country
            }) # Returns aal2 and the country --> Lugo Province
        elif aal1 and aal1 in avaliable_aal1s:      
            return ({
                'type': 'aal1',
                'locality': locality,
                'aal2': aal2,
                'aal1': aal1,
                'country': country
            }) # Ceuta "Administrative city" or "Extremadura"
        else:
            return({
                'type': 'country',
                'locality': locality,
                'aal2': aal2,
                'aal1': aal1,
                'country': country
            }) # ES if everything go wrong
    else:
        return ({
            'type': 'not_found',
            'locality': '',
            'aal2': '',
            'aal1': '', 
            'country': ''
        })
    

def get_market_from_latlng(lat,lng):
    geocode = geo_manager._get_reverse_geocoding(lat,lng)
    return get_market_from_geocode(geocode)


def get_market_from_geocode(geocode):
    return geo_manager.get_long_administrative_area_level_2_from_geocode(geocode)


@functools.lru_cache()
def get_latest_stores_from_market(type = 'locality', country = None, aal1 = None, aal2 = None, locality = None):
    return utils._anonimize_responses(store_manager._load_almarcat_stores_from_google_datastore(**locals(), limit = 24))


@functools.lru_cache()
def get_latest_items_from_market(type = 'locality', country = None, aal1 = None, aal2 = None, locality = None):
    return utils._anonimize_responses(item_manager._load_market_active_items_df_from_google_datastore(**locals(), limit = 24))


@functools.lru_cache()
def get_aal2_stores_from_market(type = 'aal2', country = None, aal1 = None, aal2 = None, locality = None):
    return utils._anonimize_responses(store_manager._load_almarcat_stores_from_google_datastore(**locals(), limit = 12))


@functools.lru_cache()
def get_aal2_items_from_market(type = 'aal2', country = None, aal1 = None, aal2 = None, locality = None):
    return utils._anonimize_responses(item_manager._load_market_active_items_df_from_google_datastore(**locals(), limit = 12))
