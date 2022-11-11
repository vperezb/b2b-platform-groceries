"""General functions usefull inside and out the project
"""

__author__ = '@vperezb'

import os
import json
import string
from io import StringIO
from html.parser import HTMLParser

import requests
import functools
import pandas as pd

import ftplib
import yaml


import csv


def read_yml(filename):
    with open(filename, 'r') as ymlfile:
        return yaml.load(ymlfile, Loader=yaml.FullLoader)


def read_file(filename, mode='r'):
    with open(filename, 'r') as myfile:
        return myfile()


def open_file(filename, mode='r'):
    with open(filename, mode) as openfile:
        return openfile.read()


def write_file(content, filename, mode='w'):
    with open(filename, mode) as openfile:
        return openfile.write(content)


def write_file_from_dict(input_dict, filename, mode='w'):
    content = json.dumps(input_dict, sort_keys=True, separators=(',', ':'))
    return write_file(content, filename)


def read_json_file(filename, mode):
    return json.loads(open_file(filename, mode))


def read_csv_to_dict_list(filename):
    with open(filename, newline='', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def read_file_to_list(filename):
    with open(filename) as f:
        content = f.readlines()
    return [x.strip() for x in content]


def get_ftp_session(credentials = None):
    if credentials is None:
            credentials = __FTP_CREDENTIALS
    return ftplib.FTP(credentials['host'], credentials['user'], credentials['password'])

def upload_to_ftp(source_filename, output_filename, credentials = None):
    if credentials is None:
            credentials = __FTP_CREDENTIALS
    ftp_session = get_ftp_session(credentials=credentials)
    file= open(source_filename, 'rb')
    ftp_session.storbinary('STOR ' + output_filename, file)
    file.close()
    return ftp_session.quit()

#from werkzeug.utils import secure_filename
def convert_to_safe_string(my_string):
    safechars = string.ascii_lowercase + string.ascii_uppercase + string.digits + '.-'
    return ''.join([c for c in my_string if c in safechars])

def _anonimize_responses(response):
    if isinstance(response, list):          
        df = pd.DataFrame.from_dict(response, orient='columns')
        if 'created_by' in df.columns: del df['created_by']
        if 'created_at' in df.columns: del df['created_at']
        if 'updated_at' in df.columns: del df['updated_at']
        if 'geocode' in df.columns: del df['geocode']
        if 'hash' in df.columns: del df['hash']
        return df.fillna('').to_dict('records')
    elif isinstance(response, pd.DataFrame):
        if 'created_by' in response.columns: del response['created_by']
        if 'created_at' in response.columns: del response['created_at']
        if 'updated_at' in response.columns: del response['updated_at']
        if 'geocode' in response.columns: del response['geocode']
        if 'hash' in response.columns: del response['hash']
        return response.fillna('').to_dict('records')
    else:
        if 'created_by' in response: del response['created_by']
        if 'created_at' in response: del response['created_at']
        if 'updated_at' in response: del response['updated_at']
        if 'geocode' in response: del response['geocode']
        if 'hash' in response: del response['hash']
        return response
    

def _transform_stores_to_geojson(response):
    
    formated_response = []

    for response_item in response:
        if (response_item['category_code_name'] != ''):
            try:
                response_item['category'] = _get_categories()[response_item['category_code_name']]
            except:
                response_item['category'] = {
                    'code_name': 'error', 'name': 'Error', 'icon': 'square-o'}
        else:
            response_item['category'] = {
                'code_name': 'other', 'name': 'Otro', 'icon': 'circle-o'}

        if ('lat' in response_item) and (response_item['lat'] not in ['null', None, '']):

            geometry = {
                "type": 'Point',
                "coordinates": [float(response_item['lng']), float(response_item['lat'])]
            }

            formated_response.append({
                'properties': response_item,
                'type': 'Feature',
                'geometry': geometry,
            })
        else:
            formated_response.append({
                'properties': response_item,
                'type': 'Feature'
            })

    return {
        "type": "FeatureCollection",
        "features": formated_response
    }


@functools.lru_cache()
def _get_categories() -> dict:
    categories_df = pd.DataFrame.from_records(requests.get('https://static.html.almarcat.com/mvp/configs/categories.json').json())
    categories_df.rename(columns={'id':'code_name', }, inplace=True)
    categories_df.set_index('code_name', drop=False, inplace=True)
    return categories_df.to_dict(orient="index")


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()



def split_dataframe(df, chunk_size = 10000): 
    chunks = list()
    num_chunks = len(df) // chunk_size + 1
    for i in range(num_chunks):
        chunks.append(df[i*chunk_size:(i+1)*chunk_size])
    return chunks