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

def _issue_request(method, relative_url, **kwargs):
    """
    Generic method for making requests to the Graph API and deserializing
    the response. Here we aggregate all general error-handling & exception
    catching/raising.

    Returns: deserialized JSON as native Python data structures.
    """
    data = {}

    url = BASE_GRAPH_URL + ('/%s' % relative_url)
    try:
        r = requests.request(method, url,
            timeout=TIMEOUT, config=REQUESTS_CONFIG, **kwargs)
    except (SSLError, Timeout) as e:
        raise FBConnectionException(e.message)

    if r.status_code != requests.codes.ok:
        raise FBHTTPException(r.status_code, r.text)

    try:
        data = json.loads(r.text)
    except ValueError as e:
        log.warn("Error decoding JSON: {0}. JSON={1}".format(e.message, r.text))
        raise FBJSONException("%s (%s)" % (e.message, r.text))

    return data

#TODO: PUT, DELETE request factories

class FBGraph(object):
    def __init__(self, access_token=''):

        self._access_token = access_token
        self._response_fmt = 'json'

    def get(self, relative_url, params=None):
        """
        Query facebook's graph api at relative_url with
        query string parameters params, where params is a python dict.
        """
        data = {}
        params = params or {}
        params['access_token'] = self._access_token

        data = _issue_request('get', relative_url, params=params)

        return data
    
    def post(self, relative_url, payload=None):
        """
        Publish to the graph.
        Returns a deserialized python object, see
        `Graph API<https://developers.facebook.com/docs/reference/api/>`_
        
        Note: this method requires a valid access token to work.
        
        Example 1::
           data = fbg.post('me/feed', {'message': 'Hello, Facebook World!'})
           print data
           # {u'id': u'537208670_111222333444555666777'}
        
        Example 2::
        
           new_pic = open('my_pic.png', 'rb')
           data = fbg.post('me/photos', {
              'source': new_pic,
              'message': 'Hey, I\'m posting a picture on Facebook!'})
           print data
           # {u'id': u'123456789012', u'post_id': u'537208670_123456789012'}
        """
        if not isinstance(payload, dict):
            raise FBException('Must specify payload as dict.')

        files = {}
        for k in payload.keys():
            if isinstance(payload[k], file):
                files[k] = payload[k]
                del payload[k]

        payload = payload or {}
        payload['access_token'] = self._access_token
        
        data = _issue_request('post', relative_url, data=payload, files=files)

        return data

    def batch(self, batch):
        """
        Query's facebook's graph api in batches. batch is a list of dicts,
        where each dict is of the form::
        
           {'method': 'GET', 'relative_url': 'someurl', ...}.
           
        There are optional params available, see:
        https://developers.facebook.com/docs/reference/api/batch/

        Returns a list of completely deserialized python data structures for
        each batch response, of the form:
            [
                {
                    "headers": [{ ... }],
                    "code": 200,
                    "body": { ... }
                },
                ...
            ]

        If there was an error in an individual response, the "body" will
        contain the deserialized Facebook error response.
        See: https://developers.facebook.com/docs/reference/api/batch/
        """
        data = []
        payload = {
            'batch': json.dumps(batch),
            'access_token': self._access_token
        }

        data = _issue_request('post', '', data=payload)
        
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
    def __init__(self, access_token):
        self._access_token = access_token
        # currrently only support json response format
        self._response_fmt = 'json'

    def query(self, fql_str):
        data = {}
        params = {
            'q': fql_str,
            'access_token' : self._access_token,
            'format': self._response_fmt
        }

        start_time = time.time()

        data = _issue_request('get', 'fql', params=params)

        stop_time = time.time()
        duration = stop_time - start_time
        data['query_time'] = duration

        return data
