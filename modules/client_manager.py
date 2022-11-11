import functools

from google.cloud import datastore, storage

from modules import config_manager

@functools.lru_cache()
def _get_google_datastore_client():
    return datastore.Client(config_manager._get_config('basic', 'infra', 'project_name'))

@functools.lru_cache()
def _get_google_storage_client():
    return storage.Client()