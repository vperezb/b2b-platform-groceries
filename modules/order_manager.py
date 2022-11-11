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

from modules import client_manager, file_manager, store_manager, utils, market_manager, geo_manager, item_manager


def _load_orders_made_by_me_from_google_datastore(store_id) -> pd.DataFrame:
    logging.info(f"Loading store from Google Datastore for user '{store_id}'...")

    google_datastore_client = client_manager._get_google_datastore_client()

    q = google_datastore_client.query(kind="order")
    q.add_filter("ordered_by_store_id", "=", store_id)
    results = list(q.fetch(limit=100))
    return results


def _load_orders_made_to_me_from_google_datastore(store_id) -> pd.DataFrame:
    logging.info(f"Loading store from Google Datastore for user '{store_id}'...")

    google_datastore_client = client_manager._get_google_datastore_client()

    q = google_datastore_client.query(kind="order")
    q.add_filter("ordered_to_store_id", "=", store_id)
    results = list(q.fetch(limit=100))
    return results

def _load_single_order_from_google_datastore(order_id: str = None) -> dict:
    logging.info(
        f"Loading store from Google Datastore for store '{order_id}'...")

    if (order_id is None or order_id == ''):
        return {}

    else:
        google_datastore_client = client_manager._get_google_datastore_client()
        #key = google_datastore_client.key("order",order_id)
        q = google_datastore_client.query(kind='order')
        q.add_filter('id', '=', order_id)
        return list(q.fetch(limit=1))[0]


def _put_order_to_google_datastore(*, order_id=None, **kwargs):

    google_datastore_client = client_manager._get_google_datastore_client()

    entity = datastore.Entity(key=google_datastore_client.key("order"))

    data_to_put = dict(
        id=uuid.uuid4().hex,
        updated_at=datetime.datetime.utcnow(),
        created_at=datetime.datetime.utcnow(),
        **kwargs
    )

    entity.update(data_to_put)

    logging.debug(
        f"Sending store to Google Data Store (event: '{entity}')...")

    google_datastore_client.put(entity)
    return data_to_put



def _put_order_to_google_datastore_from_form_info(request, user_data) -> dict:

    order_id = None
    
    if 'id' in request.form:
        order_id = request.form["id"]
    
    my_store = store_manager._load_my_stores_from_google_datastore(user_data['email'])[0]
    
    if not my_store:
        return flask.redirect(flask.url_for('home'))

    item_lines = []
    amount_to_pay = 0

    print ('HELLOEEE')
    for key, value in request.form.items():
        if key.startswith('itemQty'):
            id_item = key.replace('itemQty','')
            this_item = dict(item_manager._load_single_item_from_google_datastore(id_item))
            print (this_item['price_now'])
            if this_item:
                if int(value) != 0:
                    this_line = {
                        'item_id': id_item,
                        'title': this_item['title'],
                        'image': this_item['images'][0],
                        'qty': int(value),
                        'price_unit': this_item['price_unit'],
                        'price': float(this_item['price_now']),
                        'total': int(value) * float(this_item['price_now'])
                    }
                    item_lines.append(this_line) 
                    amount_to_pay += this_line['total']
    

    data_to_put = dict(
        ordered_by_store_id= my_store['id'],
        order_by_user= user_data['email'],
        ordered_to_store_id= request.form["ordered_to_store_id"],
        delivery_date = request.form["delivery_date"],
        item_lines=item_lines,
        amount_to_pay=amount_to_pay,
        comment=request.form["comment"].strip(),
        status='ordered',
        #delivery_method = request.form["delivery_method"],
        friendly_id = '{}-({})->{}'.format(my_store['code_name'], request.form["delivery_date"], request.form["ordered_to_store_code_name"]),
        )

    _put_order_to_google_datastore(
        order_id=order_id, **data_to_put)


    return data_to_put
