#!/usr/bin/env python3

import urllib.parse
import requests

import json
from pprint import pprint


## ------------------------------------------------------------------------
## CONSTS

## NB: Archive.org index runs on ElasticSearch
BACKEND_TYPE = 'lucene'


## ------------------------------------------------------------------------
## PRIVATE HELPERS - API - SEARCH

URL_PREFIX = 'https://archive.org/advancedsearch.php'

DEFAULT_RETURNED_FIELDS = ['identifier', 'title', 'mediatype', 'collection']

## NB: need to use old school URL encoding instead of `urllib.parse.quote_plus()`
def urlencode_basic(s):
    return s.translate(str.maketrans({' ': '+', ':': '%3A'}))

def search_raw(q, nb_items=15, returned_fields=DEFAULT_RETURNED_FIELDS):
    payload = {
        'q': urlencode_basic(q),
        'fl[]': returned_fields,
        'rows': nb_items,
        'output': 'json',
    }

    urlsuffix_list = []
    for k, v in payload.items():
        if isinstance(v, list):
            for v_e in v:
                urlsuffix_list.append(k + '=' + str(v_e))
        else:
            urlsuffix_list.append(k + '=' + str(v))
    urlsuffix = '&'.join(urlsuffix_list)

    # NB: need to use ES old school URL encoding, so can't use requests' params option
    # r = requests.get(URL_PREFIX, params=payload)
    r = requests.get(URL_PREFIX, params=urlsuffix)

    return r.json()


## ------------------------------------------------------------------------
## MAIN CLASS

## https://archive.org/advancedsearch.php#raw

class ArchiveOrgApi():

    # -------------------
    # CONSTS

    BACKEND_TYPE = BACKEND_TYPE


    # -------------------
    # LIFECYCLE

    def __init__(self, db_path=BACKEND_TYPE):
        self.db_path = db_path


    # -------------------
    # FIELDS

    FIELD_CONVERTION = {
        'authors': 'creator',
        'publishers': 'publisher',
        'pub_date': 'publicdate',

        'name': 'title',
        'subjects': 'subject',
        'series': 'collection',

        'ISBN': 'ISBN',
        'LCCN': 'LCCN',

        'item_id': 'identifier',
    }

    def corresponding_field(self, std_field):
        if std_field in self.FIELD_CONVERTION:
            return self.FIELD_CONVERTION[std_field]

    SEARCH_TYPE_FIELDS = {
        'author': ['creator'],
        'publisher': ['publisher'],
        'title': ['title'],
        'subject': ['subject'],
        'word': ['creator', 'publisher', 'title', 'subject', 'collection'],
        'series': ['collection'],
        'universal_id': ['isbn',
                         # 'lccn'
                         ],
        'item': ['identifier'],
        'bib': ['identifier'],
    }

    def search_type_corresponding_fields(self, search_type):
        if search_type in self.SEARCH_TYPE_FIELDS:
            return self.SEARCH_TYPE_FIELDS[search_type]


    # -------------------
    # ITEMS

    def item_list(self, fetch_mode='iter', fetch_format='v', where="",
                  detailed=False):
        if fetch_format == 'count':
            res = search_raw(where,
                             # NB: 1 as 0 would fallback to default pagination value
                             nb_items=1,
                             # NB: similarly, [] would fallback to all standard fields
                             returned_fields=['identifier'])
            return res['response']['numFound']
        else:
            raw_res = search_raw(where,
                             nb_items=10,
                             returned_fields=[''])
            # raise Exception(json.dumps(raw_res))
            res = {}

            field_2_std = {v: k for k, v in self.FIELD_CONVERTION.items()}

            for raw_item in raw_res['response']['docs']:
                item = {
                    'authors': ['unknown'],
                    'publishers': ['unknown'],
                    'pub_date': '????',
                    'name': 'unknown',
                    'subjects': [],
                    'series': [],
                }
                for k, v in raw_item.items():
                    if k in field_2_std:
                        item[field_2_std[k]] = v
                # NB: when only 1 author/publisher, gets returned as a string instead of array
                if isinstance(item['authors'], str):
                    item['authors'] = [item['authors']]
                if isinstance(item['publishers'], str):
                    item['publishers'] = [item['publishers']]
                res[item['item_id']] = item
            # raise Exception(json.dumps(res))
            return res
