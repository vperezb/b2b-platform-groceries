import datetime
import functools
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
#from google.cloud import bigquery

from modules import utils, client_manager

# Services Storage

ALLOWED_EVENT_NAMES = ['visit', 'product_click']
_google_cloud_project_name = "almarcat-sandbox-projects"


'''
@functools.lru_cache()
def _get_google_bigquery_client():
    return bigquery.Client(_google_cloud_project_name)'''


def _store_event_to_google_datastore(event_name, store_id):

    if event_name not in ALLOWED_EVENT_NAMES:
        return {"success": False,
                "traceback": "Event name not allowed"}

    else:
        try:
            google_datastore_client = client_manager._get_google_datastore_client()
            entity = datastore.Entity(
                key=google_datastore_client.key(
                    'Name', event_name,
                    'Store', store_id,
                    'event'
                )
            )

            entity.update({
                'timestamp': datetime.datetime.now(),
                'page_type': 'store'
            })

            google_datastore_client.put(entity)
            return {"success": True}
        except:
            return {"success": False,
                    "traceback": "Unknown error"}


def v2__store_event_to_google_datastore(event_data):
    google_datastore_client = client_manager._get_google_datastore_client()
    entity = datastore.Entity(
        key=google_datastore_client.key(
            'Name', event_data.pop('event_name', None),
            'Store', event_data.pop('store_id', None),
            'event'
        )
    )
    
    event_data['timestamp'] = datetime.datetime.now()

    entity.update(event_data)

    google_datastore_client.put(entity)
    return {"success": True}

    try:
        google_datastore_client = client_manager._get_google_datastore_client()
        entity = datastore.Entity(
            key=google_datastore_client.key(
                'Name', event_data.pop('event_name', None),
                'Store', event_data.pop('store_id', None),
                'event'
            )
        )
        
        event_data['timestamp'] = datetime.datetime.now()

        entity.update(event_data)

        google_datastore_client.put(entity)
        return {"success": True}
    except:
        return {"success": False,
                "traceback": "Unknown error"}

'''
def _store_event_to_google_bigquery(event_data):
   
    try:
        google_bigquery_client = _get_google_bigquery_client()
        
        google_bigquery_client.insert_rows_json('statistics.' + event_data.pop('event_name', None), [event_data])

        return {"success": True}
    except Exception as e:
        # "Unknown error when storing event, see logs for more info."
        return {"success": False, "traceback": 'Something happened when storing the event into the bbdd' }, 500 '''


def get_visits_df(store_id):
    google_datastore_client = client_manager._get_google_datastore_client()
    key = google_datastore_client.key(
        "Name", 'store_view',
        "Store", store_id
    )
    query = google_datastore_client.query(kind='event', ancestor=key)
    query.add_filter("timestamp", ">=",
                     datetime.datetime.utcnow() - datetime.timedelta(days=30))
    results = query.fetch()
    df = pd.DataFrame(results)
    if not df.empty:
        df['day_to_plot'] = df['timestamp'].dt.strftime('%Y-%m-%d')
        del df['timestamp'] 
        grouped = df.groupby(['day_to_plot']).count()
        grouped['TOTAL'] = grouped.sum(axis=1)
        return grouped

    else:
        return df


def _get_labels_and_visits_values(df):
    df.sort_values('day_to_plot')
    return {'labels': list(df.index), 'data': list(df['TOTAL'])}


# https://www.chartjs.org/samples/latest/charts/area/line-stacked.html