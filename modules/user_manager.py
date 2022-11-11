import google.oauth2.id_token
from google.auth.transport import requests

firebase_request_adapter = requests.Request()


def _get_authorisation(id_token):
    claims = google.oauth2.id_token.verify_firebase_token(
        id_token, firebase_request_adapter)
    if 'name' not in claims:
        claims['name'] = claims['email'].split('@')[0]
    return(claims)
