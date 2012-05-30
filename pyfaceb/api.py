import requests
import json
import time
import logging
from requests.exceptions import SSLError, Timeout

from .exceptions import (FBException, FBHTTPException, FBJSONException,
    FBConnectionException)

BASE_GRAPH_URL = "https://graph.facebook.com"
BASE_FQL_URL = "https://graph.facebook.com/fql?"
BATCH_QUERY_LIMIT = 50
TIMEOUT = 60.0
REQUESTS_CONFIG = {'max_retries': 2}

log = logging.getLogger(__name__)

def GetRequestFactory(relative_url, **params):
    ''' Returns a properly formed GET request dictionary. '''

    params['method'] = 'GET'
    params['relative_url'] = relative_url

    return params

def _issue_request(method, url, **kwargs):
    """
    Generic method for making requests to the Graph API and deserializing
    the response. Here we aggregate all general error-handling & exception
    catching/raising.

    Returns: deserialized JSON as native Python data structures.
    """
    data = {}

    try:
        r = requests.request(method, url,
            timeout=TIMEOUT, config=REQUESTS_CONFIG, **kwargs)
    except (SSLError, Timeout) as e:
        raise FBConnectionException(e.message)

    if r.status_code != requests.codes.ok:
        raise FBHTTPException(r.text)

    try:
        data = json.loads(r.text)
    except ValueError as e:
        log.warn("Error decoding JSON: {0}. JSON={1}".format(e.message, r.text))
        raise FBJSONException(e.message)

    return data

#TODO: PUT, DELETE request factories

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
        Query facebook's graph api using an object_id, and optional connection and
        query string parameters, where params is a python dict.
        '''
        data = {}
        params['access_token'] = self._access_token

        path = self._emit_graph_url(object_id, connection)
        data = _issue_request('get', path, params=params)

        return data
    
    def post(self, object_id, connection='', payload={}):
        '''
        Publish to the graph.
        Returns a deserialized python object, see `Graph API<https://developers.facebook.com/docs/reference/api/>`_
        
        Note: this method requires a valid access token to work.
        
        Example 1::
           data = fbg.post('me', 'feed', {'message': 'Hello, Facebook World!'})
           print data
           # {u'id': u'537208670_111222333444555666777'}
        
        Example 2::
        
           new_pic = open('my_pic.png', 'rb')
           data = fbg.post('me', 'photos', {
              'source': new_pic,
              'message': 'Hey, I\'m posting a picture on Facebook!'})
           print data
           # {u'id': u'123456789012', u'post_id': u'537208670_123456789012'}
        '''
        files = {}
        for k in payload.keys():
            if isinstance(payload[k], file):
                files[k] = payload[k]
                del payload[k]
                
        payload['access_token'] = self._access_token
        
        path = self._emit_graph_url(object_id, connection)
        data = _issue_request('post', path, data=payload, files=files)

        return data

    def batch(self, batch):
        '''
        Query's facebook's graph api in batches. batch is a list of dicts, where each
        dict is of the form::
        
           {'method': 'GET', 'relative_url': 'someurl', ...}.
           
        There are optional params available, see: https://developers.facebook.com/docs/reference/api/batch/
        '''
        data = []
        payload = {'batch': json.dumps(batch), 'access_token': self._access_token}

        data = _issue_request('post', BASE_GRAPH_URL, data=payload)
        
        # deserialize the body of each batch response, need to make sure it
        # is deserializable, thanks to this bug:
        # https://developers.facebook.com/bugs/295201867209494
        for d in data:
            if isinstance(d, dict) and 'body' in d:
                try:
                    d['body'] = json.loads(d['body'])
                except Exception as e:
                    log.warn("Error decoding JSON in batched request: {0}".format(e.message))
                    d['body'] = {'data': []} # default in case deserialization fails
                    pass
        
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

        data = _issue_request('get', BASE_FQL_URL, params=params)

        stop_time = time.time()
        duration = stop_time - start_time
        data['query_time'] = duration

        return data
