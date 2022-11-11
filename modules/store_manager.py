import datetime
import io
import json
import logging
import os
import urllib.parse
from typing import *
import uuid

import pandas as pd
import pytz
import requests
from google.cloud import datastore
import flask

from modules import client_manager, file_manager, geo_manager, config_manager, market_manager


__contact_mail = config_manager._get_config('basic', 'store', 'contact_mail')

# READ STORES

def _load_stores_from_google_datastore() -> List:
    logging.info(f"Loading random stores from Google Datastore ...")
    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="store")
    results = list(q.fetch(limit=150))
    return results


def _load_my_stores_from_google_datastore(user) -> pd.DataFrame:
    logging.info(f"Loading store from Google Datastore for user '{user}'...")

    google_datastore_client = client_manager._get_google_datastore_client()

    q = google_datastore_client.query(kind="store")
    q.add_filter("created_by", "=", user)
    results = list(q.fetch(limit=100))
    return results


def _load_area_stores_from_google_datastore(mgrs_4 = None, mgrs_6 = None, mgrs_8 = None) -> List:
    logging.info(f"Loading last stores from Google Datastore ...")
    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="store")
    if mgrs_4: q.add_filter('mgrs_4', '=', mgrs_4)
    elif mgrs_8: q.add_filter('mgrs_8', '=', mgrs_8)
    elif mgrs_6: q.add_filter('mgrs_6', '=', mgrs_6)
    results = list(q.fetch())
    return results


def _load_market_stores_from_google_datastore(country: str = None, market: str = None , limit = 100) -> pd.DataFrame:
    logging.info(f"Loading last stores from Google Datastore ...")
    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="store")
    q.add_filter('is_verified', '=', True)
    q.add_filter('country', '=', country)
    q.add_filter('market', '=', market)
    q.order = ['-created_at']
    return  pd.DataFrame(q.fetch(limit=limit))

def _load_almarcat_stores_from_google_datastore(type = None, country: str = None, aal1: str = None, aal2: str = None, locality: str = None , limit = 100) -> pd.DataFrame:
    logging.info(f"Loading last stores from Google Datastore ...")
    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="store")
    q.add_filter('is_verified', '=', True)
    q.add_filter('country', '=', country)
    if type == 'locality':
        q.add_filter('locality', '=', locality)
    elif type == 'aal2':
        q.add_filter('aal2', '=', aal2)
    if aal1:
        q.add_filter('aal1', '=', aal1)
    q.order = ['-created_at']
    return  pd.DataFrame(q.fetch(limit=limit))

# READ SINGLE STORE

def _load_store_by_code_name_from_google_datastore(code_name: str) -> dict:
    logging.info(
        f"Loading store from Google Datastore for store '{code_name}'...")
    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="store")
    q.add_filter("code_name", "=", code_name)
    results = q.fetch(limit=1)
    try:
        return next(iter(results))
    except StopIteration as error:
        return {}


def _load_store_by_store_id_from_google_datastore(store_id: str) -> List:
    logging.info(
        f"Loading store from Google Datastore for store '{store_id}'...")
    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="store")
    q.add_filter("id", "=", store_id)
    results = list(q.fetch(limit=1))
    if not results:
        return [{}]
    return results


def _load_store_by_code_name_if_authorised(code_name, user_data):
    authorised_store = _load_store_by_code_name_from_google_datastore(code_name)
    if not (authorised_store['created_by'] == user_data['email']):
        return False
    else:
        return authorised_store


def _load_store_by_store_id_if_authorised(store_id, user_data):
    my_stores = _load_store_by_store_id_from_google_datastore(store_id)
    if not (my_stores[0]['created_by'] == user_data['email']):
        return {}
    else:
        return my_stores[0]


def _get_store_id_by_code_name(code_name):
    google_datastore_client = client_manager._get_google_datastore_client()

    q = google_datastore_client.query(kind="store")
    q.add_filter("code_name", "=", code_name)
    results = list(q.fetch(limit=1))
    if not results:
        return None
    return results[0]['id']


def _load_store_sons_from_google_datastore(store_code_name) -> List:
    logging.info(f"Loading last stores from Google Datastore ...")
    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="store")
    q.add_filter("belongs_to", '=' , store_code_name)
    results = list(q.fetch(limit=150))
    #results = pd.DataFrame(q.fetch(limit=500))
    return results
    

def _load_last_stores_from_google_datastore(country) -> List:
    
    logging.info(f"Loading last stores from Google Datastore ...")
    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="store")
    q.add_filter('country', '=', country)
    q.add_filter('is_verified', '=', True)
    q.order = ['-created_at']
    results = list(q.fetch(limit=100))
    return results


# WRITE

def _put_store_to_google_datastore(store_id=None, **kwargs):

    google_datastore_client = client_manager._get_google_datastore_client()

    # Store no existe, la voy a crear
    if store_id is None or store_id == '':
        store_id = uuid.uuid4().hex

        entity = datastore.Entity(key=google_datastore_client.key(
            "store"
        ))

        data_to_put = dict(
            id=store_id,
            created_at=datetime.datetime.utcnow(),
            **kwargs
        )

        entity.update(data_to_put)

        logging.debug(f"Sending store to Google Data Store (event: '{entity}')...")

        google_datastore_client.put(entity)
        return data_to_put

    # Si existe, procedemos a actualizarla con los nuevos **kwargs
    else:
        my_store_authorised = _load_store_by_store_id_from_google_datastore(store_id=store_id)[0]
        # Recupero la key de la tienda que voy a editar
        entity_to_update = google_datastore_client.get(my_store_authorised.key)
        entity_to_update['id'] = store_id
        entity_to_update.update(**kwargs)
        google_datastore_client.put(entity_to_update)
        return entity_to_update


def _put_store_to_google_datastore_from_form_info(request, user_data):    
    code_name = str(request.form["code_name"]).strip().lower()
    safe_code_name = None
    codename_exists = _load_store_by_code_name_from_google_datastore(
        code_name) # {} if false

    # If has store_id means we are editing an already existing store
    store_id = request.form['store_id']
    if store_id:
        # I'm trying to edit a store by store_id
        my_authorised_store = _load_store_by_store_id_if_authorised(
            store_id, user_data)

        # If I have no authorised store -> I'm trying to hack -> Friendly message
        if my_authorised_store == {}:
            flask.flash(u'No deberías haber llegado aqui jeje 🙄, si encuentras alguna vulnerabilidad porfavor, envíame un correo a {}'.format(
                __contact_mail), 'info')
            return flask.redirect(flask.url_for('home'))
        else:
            # No quieres cambiar, te quedas con el mismo
            if code_name == my_authorised_store['code_name']:
                safe_code_name = my_authorised_store['code_name']
            # Quireres cambiar pero existe :(, te quedas con el mismo
            elif (code_name != my_authorised_store and codename_exists != {}):
                safe_code_name = my_authorised_store['code_name']
                flask.flash(u'El nombre de usuario {} ya está en uso, te hemos dejado el anterior para que no pierdas nada 😇. Si tienes dudas puedes contactarnos en {}'.format(
                    my_authorised_store['code_name'], __contact_mail), 'info')
            # Quieres cambiar y no existe, perfect, cambias
            else:
                safe_code_name = code_name

    # Si todavía no tienes safe_code_name es porqué estás creando una tienda nueva,
    # Si existe te asignamos un hash detrás para que puedas ir tirando
    if safe_code_name is None:
        if codename_exists != {}:
            safe_code_name = code_name + '_' + uuid.uuid4().hex[:6]
            flask.flash(u'El nombre de usuario {} ya está en uso, te hemos creado uno con un número aleatorio, puedes cambiarlo o quedarte con este 😇. Si tienes dudas puedes contactarnos en {}'.format(
                code_name, __contact_mail), 'info')
        else:
            safe_code_name = code_name

    web_page = request.form["web_page"].strip()
    if web_page:
        if not (web_page[:8] == 'https://' or web_page[:7] == 'http://'):
            web_page = 'https://' + web_page

    profile_image = request.files['profile_image']
    if profile_image.filename == '':
        if request.form['profile_image_url']:
            profile_image = request.form['profile_image_url']
        else:
            profile_image = config_manager._get_config('basic', 'store', 'profile_default_image_url')
    else:
        profile_image = file_manager.upload_file(
            profile_image, 'store_profile')


    phone = request.form["phone"].strip().replace(' ', '').replace('-', ' ').replace('.', '')
    if phone:
        phone_country_prefix = request.form["phone_country_prefix"].strip()
    else:
        phone_country_prefix = ''

    geocode = geo_manager._get_geocoding(request.form["adress"].strip())


    _put_store_to_google_datastore(
        store_id=store_id,
        is_group ="is_group" in request.form,
        code_name=safe_code_name,
        created_by=user_data['email'],
        schedules=request.form["schedules"].strip(),
        type=request.form["type"],
        name=request.form["name"].strip(),
        headline=request.form["headline"].strip(),
        description=request.form["description"].strip(),
        adress=request.form["adress"].strip(),
        mail=request.form["mail"].strip(),
        web_page=web_page,
        phone_country_prefix=phone_country_prefix,
        phone=phone,
        has_whatsapp=request.form["has_whatsapp"] == '1',
        # has_delivery="has_delivery" in request.form,
        # has_take_away="has_take_away" in request.form,
        # has_online_store="has_online_store" in request.form,
        # primary_color=request.form["primary_color"].strip(),
        # primary_action=request.form['primary_action'],
        profile_image=profile_image,
        lat=request.form["lat"].strip(),
        lng=request.form["lng"].strip(),
        hash = uuid.uuid4().hex,
        geocode = geocode,
        country=geo_manager.get_short_country_from_geocode(geocode),
        aal1=geo_manager.get_long_administrative_area_level_1_from_geocode(geocode),
        aal2=geo_manager.get_long_administrative_area_level_2_from_geocode(geocode),
        locality=geo_manager.get_long_locality_from_geocode(geocode)
    )


def _add_store_to_storegroup(store_code_name, storegroup_code_name, delete_mode = False):
    google_datastore_client = client_manager._get_google_datastore_client()

    my_store_authorised = _load_store_by_code_name_from_google_datastore(store_code_name)
    
    if my_store_authorised != {}:
        entity_to_update = google_datastore_client.get(my_store_authorised.key)
        if delete_mode == False:
            if ('belongs_to' in entity_to_update and entity_to_update['belongs_to']):
                entity_to_update['belongs_to'] = entity_to_update['belongs_to'].append(storegroup_code_name)
            else:
                entity_to_update['belongs_to'] = [storegroup_code_name]
            
            google_datastore_client.put(entity_to_update)
            return True
        elif delete_mode == True:
            if 'belongs_to' in entity_to_update:
                new_belongs_to = [element for element in entity_to_update['belongs_to'] if element != storegroup_code_name]
                entity_to_update['belongs_to'] = entity_to_update['belongs_to'].append(storegroup_code_name)
                google_datastore_client.put(entity_to_update)
            else:
                flask.flash(
                    u'Algo ha ido mal, no hemos podido desasignar la tienda porque no la tenías asignada.', 'warning')
                return False


    else:
        flask.flash(
                    u'No existe la tienda con el @nombre introducido!', 'warning')
        return False


def _assign_store_to_user(store_code_name, store_hash, user_data):
    google_datastore_client = client_manager._get_google_datastore_client()

    store_entity = _load_store_by_code_name_from_google_datastore(code_name=store_code_name)
    
    if store_entity != {}:
        if ('hash' in store_entity and store_entity['hash'] == store_hash):
            store_entity['created_by'] = user_data['email']
            google_datastore_client.put(store_entity)
        else:
            flask.flash(
                     u'No tienes permisos suficientes para modificar esta tienda. Si crees que es un error ponte en contacto con info@almarcat.com', 'warning')
            return False

    else:
        flask.flask(u'Parece que algo ha ido mal, ponte en contacto con info@almarcat.com para encontar una solución.', 'warning')
        return False

