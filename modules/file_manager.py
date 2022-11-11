import os
import io
import uuid
import functools
import datetime

import requests
from PIL import Image
from google.cloud import storage
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify

from modules import config_manager, client_manager

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

STORAGE_BUCKET_NAME = config_manager._get_config('basic', 'infra', 'storage_bucket_name')

IMAGE_CONFIGS = {
    'item': {
        'storage_path': 'item_image',
        'max_size': 500
    },
    'store_profile': {
        'storage_path': 'store_profile_image',
        'max_size': 1200
    },
    'store_header': {
        'storage_path': 'store_header_image',
        'max_size': 400
    }
}


def _get_image_name(filename, type):
    return _get_path_for_image_type(type) \
        + '/' + uuid.uuid4().hex \
        + '.' + _get_file_extension(filename)


def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def _get_file_extension(filename):
    try:
        return filename.rsplit('.', 1)[1].lower()
    except IndexError:
        return ''


def _get_path_for_image_type(type):
    if type in IMAGE_CONFIGS.keys():
        return IMAGE_CONFIGS[type]['storage_path']
    else:
        raise Exception(
            type + ' not in allowed types, check your allowed types')


def _get_max_size_for_image_type(type):
    if type in IMAGE_CONFIGS.keys():
        return (IMAGE_CONFIGS[type]['max_size'], IMAGE_CONFIGS[type]['max_size'])
    else:
        raise Exception(
            type + ' not in allowed types, check your allowed types')


def _get_file_content_type(filename):
    file_extension = _get_file_extension(filename)
    if file_extension in ALLOWED_IMAGE_EXTENSIONS:
        return 'image/' + file_extension
    else:
        return ''


def _upload_file_to_google_storage(file, bucket_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = client_manager._get_google_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.content_type = _get_file_content_type(destination_blob_name)
    blob.upload_from_file(file)
    return blob.public_url


def _upload_from_filename_to_google_storage(filename, bucket_name, destination_blob_name):
    """Uploads a file from a filename to the bucket."""
    storage_client = client_manager._get_google_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    content_type = _get_file_content_type(destination_blob_name)
    if content_type:
        blob.content_type = content_type
    blob.upload_from_filename(filename)
    return blob.public_url


def _upload_string_to_google_storage(string, bucket_name, destination_blob_name):
    """Uploads a string to the bucket."""
    storage_client = client_manager._get_google_storage_client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(
        string, content_type=_get_file_content_type(destination_blob_name))
    return blob.public_url


def _resize_pil_image(pil_image, max_size):
    x, y = pil_image.size
    if x > max_size[0] or y > max_size[1]:
        pil_image.thumbnail(max_size, Image.ANTIALIAS)
    else:
        pass
    return pil_image


def _get_pil_image_from_form_file(file):
    return Image.open(file.stream)


def _get_pil_image_from_url(url):
    try:
        response = requests.get(url)
        return Image.open(io.BytesIO(response.content))
    except:
        flash('No hemos podido acceder a la imagen, súbela manualmente', 'warning')
        raise Exception(
            'No hemos podido acceder a la imagen, súbela manualmente')


def _save_pil_image_to_byte_array(pil_image):
    byte_array = io.BytesIO()
    pil_image.save(byte_array, format=pil_image.format)
    return byte_array


def upload_file(file, type):
    if file and _allowed_file(file.filename):
        image = _get_pil_image_from_form_file(file)
        image = _resize_pil_image(image, _get_max_size_for_image_type(type))
        image = _save_pil_image_to_byte_array(image).getvalue()
        image_path = _get_image_name(file.filename, type)
        image_public_url = _upload_string_to_google_storage(
            image, STORAGE_BUCKET_NAME, image_path)
        return image_public_url
    else:
        return 'https://img.utdstc.com/icons/almarcat-android.png:300'


def _upload_from_url_to_storage(url_image, type):
    try:
        image = _get_pil_image_from_url(url_image)
        image_path = _get_image_name(
            'placeholder.' + image.format.lower(), type)
        image = _resize_pil_image(image, _get_max_size_for_image_type(type))
        image = _save_pil_image_to_byte_array(image).getvalue()
        image_public_url = _upload_string_to_google_storage(
            image, STORAGE_BUCKET_NAME, image_path)
        return image_public_url
    except Exception as e:
        print(e)
        return 'https://img.utdstc.com/icons/almarcat-android.png:300'


def _is_in_storage(url_image):
    return f'/{STORAGE_BUCKET_NAME}/' in url_image

def __get_signed_URL(request):
    filename = request.args.get('filename')
    action = request.args.get('action')
    storage_client = client_manager._get_google_storage_client()
    bucket = storage_client.bucket(STORAGE_BUCKET_NAME)
    blob = bucket.blob(filename)
    url = blob.generate_signed_url(
        expiration=datetime.timedelta(minutes=30),
        method=action, version="v4")
    return url