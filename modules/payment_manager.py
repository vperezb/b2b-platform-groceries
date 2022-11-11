from typing import *
import logging
import functools
import datetime
import requests
import json
import urllib.parse
from http import HTTPStatus
from flask import jsonify
from google.cloud import datastore

# Services Storage

_google_cloud_project_name = "almarcat-sandbox-projects"

# Paypal credentials

### PRODUCTION ###
_client_id = "id"
_client_secret = "secret"

# Paypal URLs

### SANDBOX ###
# _paypal_server = "https://api.sandbox.paypal.com"

### PRODUCTION ###
_paypal_server = "https://api.paypal.com"

# Paypal methods

def get_paypal_url(url_mode: str, order_id:str = None) -> str:
  if (url_mode == "TOKEN" ):
    return urllib.parse.urljoin(_paypal_server, '/v1/oauth2/token') 
  if (url_mode == "ORDERS"):
    if order_id is None:
      return urllib.parse.urljoin(_paypal_server, '/v2/checkout/orders') 
    else:
      return urllib.parse.urljoin(_paypal_server, f"/v2/checkout/orders/{order_id}/capture") 

def get_token():

    d = {"grant_type": "client_credentials"}
    h = {"Accept": "application/json", "Accept-Language": "en_US"}

    r = requests.post(get_paypal_url("TOKEN"),
                      data=d,
                      auth=(_client_id, _client_secret),
                      headers=h)

    return r.json()['access_token']


def build_create_order_request_body(order_unit):
  """Method to create body with a custom PAYEE (receiver)
     Info: https://developer.paypal.com/docs/api/orders/v2/

     You can patch these attributes and objects to complete these operations:
        intent — replace.
        purchase_units — replace, add.
        purchase_units[].custom_id — replace, add, remove.
        purchase_units[].description — replace, add, remove.
        purchase_units[].payee.email — replace.
        purchase_units[].shipping.name — replace, add.
        purchase_units[].shipping.address — replace, add.
        purchase_units[].soft_descriptor — replace, remove.
        purchase_units[].amount — replace.
        purchase_units[].invoice_id — replace, add, remove.
        purchase_units[].payment_instruction — replace.
        purchase_units[].payment_instruction.disbursement_mode — replace. (By default, disbursement_mode is INSTANT.)
        purchase_units[].payment_instruction.platform_fees — replace, add, remove.
  """

  print(f"\n\order_unit: {order_unit}\n\n")

  request_body = {}

  request_body['intent'] = "CAPTURE"
  request_body['purchase_units'] = []

  purchase_unit = {}

  purchase_unit['amount'] = {
      "currency_code": f"{order_unit['currency_code']}",
      "value": f"{float(order_unit['amount_value']) * int(order_unit['quantity'])}",
      "breakdown":  {
        "item_total": {
          "currency_code": f"{order_unit['currency_code']}",
          "value": f"{float(order_unit['amount_value']) * int(order_unit['quantity'])}"
        },
        "discount": {
          "currency_code": f"{order_unit['currency_code']}",
          "value": "0"
        }
      }
    }        

  purchase_unit['items'] = []
  item = {
    "name": f"{order_unit['description']}",
    "unit_amount": {
      "currency_code": f"{order_unit['currency_code']}",
      "value": f"{order_unit['amount_value']}"
    },
    "quantity": f"{order_unit['quantity']}"
  }
  purchase_unit['items'].append(item)
    
  purchase_unit['description'] = f"{order_unit['description']}"    
  purchase_unit['reference_id'] = f"{order_unit['reference_id']}"

  if (order_unit['custom_id'] is not None):
    purchase_unit['custom_id'] = order_unit['custom_id']

  request_body['purchase_units'].append(purchase_unit)

  print(f"\n\nrequest_body: {request_body}\n\n")

  return request_body

def create_order(order_units):

  token = get_token()
  request_body = build_create_order_request_body(order_units)

  d = json.dumps(request_body)
  h = {
      "Content-Type": "application/json",
      "Prefer": "return=representation",
      "Authorization": f"Bearer {token}"}

  r = requests.post(get_paypal_url("ORDERS"),
                    data=d,
                    headers=h)

  if r.status_code == HTTPStatus.CREATED:
    res = r.json()
    print(f"\n\ncreate_order_response: {res}\n\n")
    print(f"Order {res['id']} created successfully!")
  else:
    print(r.text)

  return r.json()

def capture_order(order_id: str):

    token = get_token()

    h = {"Content-Type": "application/json",
         "Authorization": f"Bearer {token}"}

    r = requests.post(get_paypal_url("ORDERS", order_id),
                      headers=h)

    response = r.json()

    if r.status_code == HTTPStatus.CREATED:
      print(f"\n\ncaptured_order_response: {response}\n\n")
      print(f"Order {response['id']} captured successfully!")
    else:
      print(r.text)

    return response

# Data storage

@functools.lru_cache()
def _get_google_datastore_client():
    return datastore.Client(_google_cloud_project_name)


def _load_order_by_id_from_google_datastore(order_id: str) -> List:
    logging.info(
        f"Loading order {order_id} from Google Datastore...")
    google_datastore_client = _get_google_datastore_client()
    q = google_datastore_client.query(kind="order")
    q.add_filter("order_id", "=", order_id)
    results = list(q.fetch(limit=1))
    if not results:
        return [{}]
    return results

def _update_order_captured_to_google_datastore(paypal_response, **kwargs):

    google_datastore_client = _get_google_datastore_client()
    order_id = paypal_response['id']
    existing_order = _load_order_by_id_from_google_datastore(order_id)[0]
   
    # Recupero la key del pedido que voy a editar
    entity_to_update = google_datastore_client.get(existing_order.key)
    entity_to_update['approved_at'] = datetime.datetime.utcnow()
    entity_to_update['order_approved_json'] = paypal_response
    entity_to_update['order_status'] = paypal_response['status']
    entity_to_update['payer_email_address'] = paypal_response['payer']['email_address']
    entity_to_update.update(**kwargs)
    google_datastore_client.put(entity_to_update)
    return entity_to_update

def _put_order_created_to_google_datastore(store_id, paypal_response, **kwargs):

    google_datastore_client = _get_google_datastore_client()

    entity = datastore.Entity(key=google_datastore_client.key(
        "order"
    ))
 
    total_amount = sum(float(o['amount']['value']) for o in paypal_response['purchase_units'])

    data_to_put = dict(
        order_id=paypal_response['id'],
        order_status=paypal_response['status'],
        created_at=datetime.datetime.utcnow(),
        store_id=store_id,
        total_amount=total_amount,
        order_created_json=paypal_response,            
        **kwargs
    )

    entity.update(data_to_put)

    logging.debug(f"Sending order to Google Data Store (event: '{entity}')...")

    google_datastore_client.put(entity)
    return data_to_put

 