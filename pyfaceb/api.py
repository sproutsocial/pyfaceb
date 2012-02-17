import urllib, urllib2
import json
import time

BASE_GRAPH_URL = "https://graph.facebook.com"
BASE_FQL_URL = "https://graph.facebook.com/fql?"
BATCH_QUERY_LIMIT = 50
TIMEOUT = 60

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

    def _emit_url_params(self, params=None):
        query_params = {}

        if params:
            query_params = params
            query_params['access_token'] = self._access_token
        else:
            query_params['access_token'] = self._access_token

        return query_params

    def _emit_graph_url(self, object_id, connection=''):
        url_fragment = '/'

        if connection != '':
            url_fragment += str(object_id) + '/' + str(connection) + '?'
        else:
            url_fragment += str(object_id) + '?'

        return url_fragment

    def get(self, object_id, connection='', params=None):
        results_dict = {}

        qry_str_enc = urllib.urlencode(self._emit_url_params(params))

        start_time = time.time()

        path = self._emit_graph_url(object_id, connection)

        try:
            results = urllib2.urlopen(BASE_GRAPH_URL + path + qry_str_enc, timeout=TIMEOUT).read()
        except urllib2.HTTPError as e:
            results = e.read()

        if results != '[]':
            results_dict = json.loads(results)

        stop_time = time.time()
        duration = stop_time - start_time
        results_dict['query_time'] = duration

        return results_dict

    def get_batch(self, batch):
        results_dict = {}

        qry_str_enc = urllib.urlencode(self._emit_url_params({'batch': batch}))

        start_time = time.time()

        # POST the data, batch queries must be POSTed
        try:
            results = urllib2.urlopen(BASE_GRAPH_URL, qry_str_enc, timeout=TIMEOUT).read()
        except urllib2.HTTPError as e:
            results = e.read()

        if results != '[]':
            results_dict = json.loads(results)

        stop_time = time.time()
        duration = stop_time - start_time
        #TODO: Figure out what to do for this...batch queries returns an array
        #of responses, not a dict like the basic graph API calls...
        #results_dict['query_time'] = duration

        return results_dict


class FBQuery(object):
    def __init__(self, access_token=''):
        self._access_token = access_token
        # currrently only support json response format
        self._response_fmt = 'json'

    def _emit_qry_url_parms(self, qry):
        return {'q': qry, 'access_token' : self._access_token,
                'format': self._response_fmt}

    def query(self, fql_str=None):
        results_dict = {}
#try:
        if fql_str:
            fql_str_enc = urllib.urlencode(self._emit_qry_url_parms(fql_str))

            start_time = time.time()

            try:
                results = urllib2.urlopen(BASE_FQL_URL + fql_str_enc, timeout=TIMEOUT).read()
            except urllib2.HTTPError as e:
                results = e.read()

            if (results != '[]'):
                results_dict = json.loads(results)

            stop_time = time.time()
            duration = stop_time - start_time
            results_dict['query_time'] = duration
        else:
            raise Exception

        return results_dict
#except:
