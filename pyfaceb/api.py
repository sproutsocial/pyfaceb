import requests
import json
import time

from . import FBException

BASE_GRAPH_URL = "https://graph.facebook.com"
BASE_FQL_URL = "https://graph.facebook.com/fql?"
BATCH_QUERY_LIMIT = 50
TIMEOUT = 60.0
REQUESTS_CONFIG = {'max_retries': 2}

def GetRequestFactory(relative_url, **params):
    ''' Returns a properly formed GET request dictionary. '''

    params['method'] = 'GET'
    params['relative_url'] = relative_url

    return params

#TODO: POST, PUT, DELETE request factories

class FBGraph(object):
    def __init__(self, access_token=''):

        self._access_token = access_token
        self._response_fmt = 'json'

    def _emit_graph_url(self, object_id, connection=''):
        url = BASE_GRAPH_URL + '/' + str(object_id)

        if connection != '':
            url += '/' + str(connection)

        return url
    
    def get(self, object_id, connection='', params={}):
        '''
        Query's facebook's graph api using an object_id, and optional connection and
        query string parameters, where params is a python dict.
        '''
        data = {}
        params['access_token'] = self._access_token

        path = self._emit_graph_url(object_id, connection)
        r = requests.get(path, params=params, timeout=TIMEOUT, config=REQUESTS_CONFIG)
        
        if r.status_code != requests.codes.ok:
            raise FBException(r.text)

        data = json.loads(r.text)

        return data

    def get_batch(self, batch):
        '''
        Query's facebook's graph api in batches. batch is a list of dicts, where each
        dict is of the form {'method': 'GET', 'relative_url': 'someurl', ...}. There
        are optional params available, see: https://developers.facebook.com/docs/reference/api/batch/
        '''
        data = []
        payload = {'batch': json.dumps(batch), 'access_token': self._access_token}

        r = requests.post(BASE_GRAPH_URL, data=payload, timeout=TIMEOUT, config=REQUESTS_CONFIG)
        
        if r.status_code != requests.codes.ok:
            raise FBException(r.text)
        
        data = json.loads(r.text)
        
        # deserialize the body of the response, need to make sure it
        # is deserializable, thanks to this bug:
        # https://developers.facebook.com/bugs/295201867209494
        for d in data:
            if isinstance(d, dict) and 'body' in d:
                d['body'] = json.loads(d['body'])
        
        return data


class FBQuery(object):
    def __init__(self, access_token=''):
        self._access_token = access_token
        # currrently only support json response format
        self._response_fmt = 'json'

    def _emit_qry_url_parms(self, qry):
        return {'q': qry, 'access_token' : self._access_token,
                'format': self._response_fmt}

    def query(self, fql_str):
        data = {}
        params = {'q': fql_str, 'access_token' : self._access_token, 'format': self._response_fmt}

        start_time = time.time()

        r = requests.get(BASE_FQL_URL, params=params, timeout=TIMEOUT, config=REQUESTS_CONFIG)
        
        if r.status_code != requests.codes.ok:
            raise FBException(r.text)

        data = json.loads(r.text)

        stop_time = time.time()
        duration = stop_time - start_time
        data['query_time'] = duration

        return data
