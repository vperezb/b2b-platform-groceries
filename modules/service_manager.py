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

from modules import file_manager, store_manager, utils

# Services Storage

_google_cloud_project_name = "almarcat-sandbox-projects"


# Private API


@functools.lru_cache()
def _get_google_datastore_client():
    return datastore.Client(_google_cloud_project_name)


def _put_service_to_google_datastore_from_form_info(service_info ,user_data) -> dict:

    service_id = None
    store_id = service_info['store_id']

    my_authorised_store = store_manager._load_store_by_store_id_if_authorised(
        store_id, user_data)

    if not my_authorised_store:
        flask.flash(
                u'No tienes permiso en esta tienda', 'danger')
        return flask.redirect(flask.url_for('home'))

    data_to_put = dict(
        created_by=user_data['email'],
        country='ES',
        #title = service_info['title'],
        status_text = 'Solicitado, Pendiente de activar',
        status_color = 'warning',
        comments = 'Contactaremos contigo para dar seguimiento.',
        #'Campaña solicitada con éxito, en el día siguiente a la activación se podrá ver el banner en almarcat.',
        #coupon_code ="", 
        #price = request.form['price'], 
        #service_code_name = request.form['service_code_name'], 
        #start_date = request.form['start_date'], 
        #end_date = request.form['end_date'], 
        #store_id = store_id,
        #to_pay = request.form['to_pay'],
        payment_status = "Pending"      
        )
        
    data_to_put.update(service_info)

    # Send the event to datastore
    _put_service_to_google_datastore(
       store_info= my_authorised_store, **data_to_put)
    
    # To be returned to the next screen
    data_to_put['store_code_name'] = my_authorised_store['code_name']
    
    return data_to_put


def _put_service_to_google_datastore(*, store_info: dict = None, **kwargs):
   
    google_datastore_client = _get_google_datastore_client()

    entity = datastore.Entity(key=google_datastore_client.key(
        "Store", store_info['id'],
        "service"
    ))

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


def _load_active_services_from_store_source_google_datastore(store_id: str = None) -> pd.DataFrame:
    logging.info(
        f"Loading store from Google Datastore for store '{store_id}'...")

    google_datastore_client = _get_google_datastore_client()
    ancestor = google_datastore_client.key('Store', store_id)
    q = google_datastore_client.query(kind="service", ancestor=ancestor)
    results = list(q.fetch(limit=100))

    return results


def _get_avaliable_services() -> list:
    country_configs_df = pd.read_csv(os.path.join("data", "avaliable_services.csv"))
    #country_configs_df.set_index("code_name", inplace=True)
    return country_configs_df.to_records()

# Pending — your payment has not been sent to the bank or credit card processor.
# Success — your credit or debit card payment has been processed and accepted.
# Complete — your checking, savings or other bank account payment has been processed and accepted.
# Cancelled — you stopped the payment before it was processed. For automatic recurring payments, all remaining payments were cancelled.
# Rejected — your payment was not accepted when it was processed by the bank or credit card company. Contact the bank or credit card company for information. Do not contact Pay.gov.