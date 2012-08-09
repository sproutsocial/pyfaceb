import requests
import json
import time
import logging
from requests.exceptions import SSLError, Timeout

from .exceptions import (FBException, FBHTTPException, FBJSONException,
    FBConnectionException)

BASE_GRAPH_URL = "https://graph.facebook.com"
BATCH_QUERY_LIMIT = 50
TIMEOUT = 60.0
REQUESTS_CONFIG = {'max_retries': 2}
VERIFY_SSL = False

log = logging.getLogger(__name__)

def GetRequestFactory(relative_url, **params):
    ''' Returns a properly formed GET request dictionary. '''

    params['method'] = 'GET'
    params['relative_url'] = relative_url

    return params

#TODO: PUT, DELETE request factories

class FBGraph(object):
    def __init__(self, access_token='', timeout=TIMEOUT,
                 pre_hook=None, post_hook=None):
        """
        :param access_token: A valid Facebook access token.
        :param timeout: Per-request HTTP timeout. Default is 60.0 seconds.
        :param pre_hook: Callable that will run before a request is made.
        :param post_hook: Callable that will run after a request is made.
        :return: FBGraph instance.
        """

        self._access_token = access_token
        self._response_fmt = 'json'
        self._timeout = timeout
        self.pre_hook = pre_hook
        self.post_hook = post_hook

    def get(self, relative_url, params=None):
        """
        Query facebook's graph api at relative_url with
        query string parameters params, where params is a python dict.
        """
        params = params or {}
        params['access_token'] = self._access_token

        data = self._issue_request('get', relative_url, params=params,
            timeout=self._timeout)

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
        
        data = self._issue_request('post', relative_url, data=payload,
            files=files, timeout=self._timeout)

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
        payload = {
            'batch': json.dumps(batch),
            'access_token': self._access_token
        }

        data = self._issue_request('post', '', data=payload,
            timeout=self._timeout)
        
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

    def _issue_request(self, method, relative_url, **kwargs):
        """
        Generic method for making requests to the Graph API and deserializing
        the response. Here we aggregate all general error-handling & exception
        catching/raising.

        Returns: deserialized JSON as native Python data structures.
        """
        url = BASE_GRAPH_URL + ('/%s' % relative_url)
        kwargs['timeout'] = kwargs.get('timeout', TIMEOUT)
        kwargs['verify'] = kwargs.get('verify', VERIFY_SSL)

        self._exec_hook('pre')
        try:
            r = requests.request(method, url, config=REQUESTS_CONFIG, **kwargs)
        except (SSLError, Timeout) as e:
            raise FBConnectionException(e.message)
        self._exec_hook('post')

        if r.status_code != requests.codes.ok:
            raise FBHTTPException(r.status_code, r.text)

        try:
            data = json.loads(r.text)
        except ValueError as e:
            log.warn("Error decoding JSON: {0}. JSON={1}".format(e.message, r.text))
            raise FBJSONException("%s (%s)" % (e.message, r.text))

        return data

    def _exec_hook(self, hook_type):
        hook = None

        if hook_type == 'pre':
            hook = self.pre_hook
        elif hook_type == 'post':
            hook = self.post_hook

        if callable(hook):
            try:
                hook()
            except Exception as e:
                log.warning('Warning: pre_hook raised %s', e.message)

