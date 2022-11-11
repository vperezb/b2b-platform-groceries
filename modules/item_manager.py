import datetime
import functools
import io
import json
import logging
import os
import urllib.parse
import uuid

import pandas as pd
import pytz
import requests
from google.cloud import datastore
from bs4 import BeautifulSoup
import flask

from modules import client_manager, file_manager, store_manager, utils, market_manager, geo_manager


def _load_active_items_by_product_type_id_from_google_datastore(product_type_id: str = None, limit = 500) -> pd.DataFrame:

    if product_type_id is None:
        return {}

    else:
        google_datastore_client = client_manager._get_google_datastore_client()
        q = google_datastore_client.query(kind="item")
        q.add_filter('product_type_id', '=', product_type_id)
        q.add_filter('is_enabled', '=', True)
        # results = pd.DataFrame(q.fetch(limit=limit))
        results = list(q.fetch(limit=limit))
        return results


def _load_items_from_google_datastore(store_id: str = None) -> pd.DataFrame:
    logging.info(
        f"Loading store from Google Datastore for store '{store_id}'...")

    if store_id is None:
        google_datastore_client = client_manager._get_google_datastore_client()
        q = google_datastore_client.query(kind="item")
        q.order = ['-created_at']
        results = list(q.fetch(limit=100))

    else:
        google_datastore_client = client_manager._get_google_datastore_client()
        ancestor = google_datastore_client.key('Store', store_id)
        q = google_datastore_client.query(kind="item", ancestor=ancestor)
        results = list(q.fetch(limit=100))

    return results


def _load_active_items_from_google_datastore(store_id: str = None) -> pd.DataFrame:
    logging.info(
        f"Loading store from Google Datastore for store '{store_id}'...")


    google_datastore_client = client_manager._get_google_datastore_client()
    ancestor = google_datastore_client.key('Store', store_id)
    q = google_datastore_client.query(kind="item", ancestor=ancestor)
    q.add_filter('is_enabled', '=', True)
    results = list(q.fetch(limit=100))

    if results:
        return results
    else:
        return []


def _change_item_enabled(store_info, item_id, is_enabled):
    google_datastore_client = client_manager._get_google_datastore_client()

    my_item = _load_single_item_from_google_datastore(item_id)

    if my_item.key.parent.name == store_info['id']:
        entity = datastore.Entity(key=my_item.key)

        print(entity)

        data_to_put = dict(
            updated_at=datetime.datetime.utcnow(),
            is_enabled=is_enabled
        )

        my_item.update(data_to_put)
        entity.update(my_item)

        logging.debug(
            f"Sending store to Google Data Store (event: '{entity}')...")

        google_datastore_client.put(entity)

        return True
    else:
        return False


def _load_featured_active_items_df_from_google_datastore(country: str = None,limit = 100) -> pd.DataFrame:
    logging.info(
        f"Loading active items from Google Datastore for country '{country}'...")

    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="item")
    q.add_filter('is_enabled', '=', True)
    q.add_filter('country', '=', country)
    return  pd.DataFrame(q.fetch(limit=limit))


def _load_active_items_df_from_google_datastore(country: str = None, limit = 100) -> pd.DataFrame:
    logging.info(
        f"Loading active items from Google Datastore for country '{country}'...")

    google_datastore_client = client_manager._get_google_datastore_client()
    q = google_datastore_client.query(kind="item")
    q.add_filter('is_enabled', '=', True)
    q.add_filter('country', '=', country)
    q.order = ['-updated_at']
    return  pd.DataFrame(q.fetch(limit=limit))


def _load_store_active_items_df_from_google_datastore(store_id: str = None, limit = 500) -> pd.DataFrame:
    logging.info(
        f"Loading store from Google Datastore for store '{store_id}'...")

    if store_id is None:
        return {}

    else:
        google_datastore_client = client_manager._get_google_datastore_client()
        ancestor = google_datastore_client.key('Store', store_id)
        q = google_datastore_client.query(kind="item", ancestor=ancestor)
        q.add_filter('is_enabled', '=', True)
        results = pd.DataFrame(q.fetch(limit=limit))
        return results


def _load_single_item_from_google_datastore(item_id: str = None) -> dict:
    logging.info(
        f"Loading store from Google Datastore for store '{item_id}'...")

    if (item_id is None or item_id == ''):
        return {}

    else:
        google_datastore_client = client_manager._get_google_datastore_client()
        #ancestor = google_datastore_client.key('Store', store_id)
        q = google_datastore_client.query(kind="item")
        q.add_filter('id', '=', item_id)
        results = list(q.fetch(limit=1))
        return results[0]


def _put_item_to_google_datastore(*, item_id=None, store_info=None, **kwargs):

    external_store_info = { key: store_info[key] for key in ['name', 'code_name', 'profile_image'] }
    
    google_datastore_client = client_manager._get_google_datastore_client()

    my_item = _load_single_item_from_google_datastore(item_id)

    # bar = kwargs.pop('bar')

    if (item_id != None and item_id != ''):
        if my_item.key.parent.name == store_info['id']:
            entity = datastore.Entity(key=my_item.key)

            data_to_put = dict(
                id=item_id,
                external_store_info = external_store_info,
                updated_at=datetime.datetime.utcnow(),
                **kwargs
            )
    else:
        entity = datastore.Entity(key=google_datastore_client.key(
            "Store", store_info['id'],
            "item"
        ))

        data_to_put = dict(
            id=uuid.uuid4().hex,
            external_store_info = external_store_info,
            updated_at=datetime.datetime.utcnow(),
            created_at=datetime.datetime.utcnow(),
            **kwargs
        )

    entity.update(data_to_put)

    logging.debug(
        f"Sending store to Google Data Store (event: '{entity}')...")

    google_datastore_client.put(entity)
    return data_to_put


def _delete_item_from_google_datastore(*, item_id=None, store_id=None, **kwargs):
    google_datastore_client = client_manager._get_google_datastore_client()

    my_item = _load_single_item_from_google_datastore(item_id)

    if item_id != None:
        if my_item.key.parent.name == store_id:
            google_datastore_client.delete(my_item.key)
    return {}


def _put_item_to_google_datastore_from_form_info(request, user_data) -> dict:

    item_id = None
    if 'id' in request.form:
        item_id = request.form["id"]

    store_code_name = request.form['store_code_name']

    my_authorised_store = store_manager._load_store_by_code_name_if_authorised(
        store_code_name, user_data)
    if not my_authorised_store:
        return flask.redirect(flask.url_for('home'))

    if my_authorised_store['geocode']['status'] == 'OK':
        country = geo_manager.get_short_country_from_geocode(my_authorised_store['geocode'])
        locality = geo_manager.get_long_locality_from_geocode(my_authorised_store['geocode'])
        aal1 = geo_manager.get_long_administrative_area_level_1_from_geocode(my_authorised_store['geocode'])
        aal2 = geo_manager.get_long_administrative_area_level_2_from_geocode(my_authorised_store['geocode'])
    else:
        country = 'ES'
        locality = geo_manager.get_long_locality_from_geocode(my_authorised_store['geocode'])
        aal1 = geo_manager.get_long_administrative_area_level_1_from_geocode(my_authorised_store['geocode'])
        aal2 = geo_manager.get_long_administrative_area_level_2_from_geocode(my_authorised_store['geocode'])

    file = request.files['picture']
    if file.filename == '':
        if "url_image" in request.form:
            if request.form["url_image"] != '':
                picture = request.form["url_image"]
                if not file_manager._is_in_storage(picture):
                    picture = file_manager._upload_from_url_to_storage(picture, 'item')
            else:
                picture = 'https://img.utdstc.com/icons/almarcat-android.png:300'
        else:
            picture = 'https://img.utdstc.com/icons/almarcat-android.png:300'
    else:
        picture = file_manager.upload_file(file, 'item')

    price_now = request.form["price_now"]
    price_unit = request.form["price_unit"]
    qty =  request.form["qty"]

    if price_now:
        price_now = format(float(price_now), '.2f')

    data_to_put = dict(
        created_by=user_data['email'],
        title=utils.strip_tags(request.form["title"].strip()),
        product_type_name=request.form["product_type_name"],
        product_type_id=request.form["product_type_id"],
        price_now=price_now,
        price_unit=price_unit,
        qty=qty,
        images=[picture],
        is_enabled="is_enabled" in request.form,
        producer= request.form["producer"],
        country= country,
        aal1 = aal1,
        aal2 = aal2,
        locality = locality
        )

    _put_item_to_google_datastore(
        item_id=item_id, store_info=my_authorised_store, **data_to_put)
    data_to_put['store_code_name'] = my_authorised_store['code_name']
    return data_to_put
