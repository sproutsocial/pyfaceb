import json
import os
import unittest

import requests
from mock import Mock
from mock import patch
from requests.exceptions import SSLError

from pyfaceb.api import FBGraph
from pyfaceb.exceptions import FBConnectionException
from pyfaceb.exceptions import FBHTTPException
from pyfaceb.exceptions import FBJSONException


FIXTURES = os.path.dirname(__file__)

class FBGraphTest(unittest.TestCase):

    def test_basic_get_personal_profile(self):
        expected = {
            u'username': u'kevin.r.stanton',
            u'first_name': u'Kevin',
            u'last_name': u'Stanton',
            u'name': u'Kevin Stanton',
            u'locale': u'en_US',
            u'gender': u'male',
            u'id': u'537208670'
        }
        fbg = FBGraph()
        result = fbg.get('kevin.r.stanton')
        self.assertDictEqual(expected, result)

    def test_basic_get_company_profile(self):
        fbg = FBGraph()
        result = fbg.get('SproutSocialInc')
        self.assertIsInstance(result, dict)
        self.assertEquals('2009', result['founded'])
        self.assertEquals('Sprout Social', result['name'])
        self.assertEquals('138467959508514', result['id'])
        self.assertEquals('SproutSocialInc', result['username'])

    @patch.object(requests, 'request')
    def test_get_with_fields_arguments(self, request):
        mock_response = Mock()
        mock_response.text = '{"talking_about_count": 309, "likes": 6201, "id": "138467959508514"}'
        mock_response.status_code = 200
        request.return_value = mock_response
        f = FBGraph()
        result = f.get(
            'sproutsocialinc', {'fields': 'likes,talking_about_count'})
        self.assertDictEqual(result, {
            "id": "138467959508514",
            "likes": 6201,
            "talking_about_count": 309
        })

    @patch.object(requests, 'request')
    def test_FBJSONException(self, request):
        mock_response = Mock()
        mock_response.text = 'i am bad json'
        mock_response.status_code = 200
        request.return_value = mock_response

        fbg = FBGraph()
        self.assertRaises(FBJSONException, fbg.get, 'me')

        try:
            fbg.get('me')
        except FBJSONException as e:
            self.assertEquals(
                'No JSON object could be decoded (i am bad json)', e.message)

    @patch.object(requests, 'request')
    def test_FBHTTPException(self, request):
        exp_fb_error = {'error': {'message': '(#1000) Facebook error message',
                                  'code': 1000}}

        mock_response = Mock()
        mock_response.text = json.dumps(exp_fb_error)
        mock_response.status_code = 400
        request.return_value = mock_response

        fbg = FBGraph()
        self.assertRaises(FBHTTPException, fbg.get, 'me')
        try:
            fbg.get('me')
        except FBHTTPException as e:
            self.assertEquals(e.code, 400)
            self.assertEquals(e.body, json.dumps(exp_fb_error))
            self.assertEquals(e.json, exp_fb_error)
            self.assertEquals(e.message, json.dumps(exp_fb_error))
            self.assertEquals(
                e.__str__(),
                'FBHTTPException(400, %s)' % json.dumps(exp_fb_error))
            self.assertEquals(
                e.__repr__(),
                'FBHTTPException(400, %s)' % json.dumps(exp_fb_error))

    @patch.object(requests, 'request')
    def test_FBHTTPException_bad_json(self, request):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'non-json error'
        request.return_value = mock_response

        fbg = FBGraph()
        self.assertRaises(FBHTTPException, fbg.get, 'me')
        try:
            fbg.get('me')
        except FBHTTPException as e:
            self.assertEquals(e.code, 400)
            self.assertEquals(e.body, 'non-json error')
            self.assertEquals(e.json, FBHTTPException.FALLBACK_ERROR_OBJ)
            self.assertEquals(e.message, 'non-json error')
            self.assertEquals(
                e.__str__(),
                'FBHTTPException(400, %s)' % 'non-json error')
            self.assertEquals(
                e.__repr__(),
                'FBHTTPException(400, %s)' % 'non-json error')

    @patch.object(requests, 'request')
    def test_FBConnectionException(self, request):
        def side_effect(*args, **kwargs):
            raise SSLError('The read operation timed out')
        request.side_effect = side_effect

        fbg = FBGraph()
        self.assertRaises(FBConnectionException, fbg.get, 'me')
        self.assertRaises(
            FBConnectionException,
            fbg.post,
            'me',
            payload={'junk': 'data'})

    @patch.object(requests, 'request')
    def test_batch_with_individual_rqst_errors(self, request):
        """
        Ensure that when single requests in the batch contain an
        error, the error json is deserialized properly and returned
        for individual requests.
        """
        fixture = 'test_batch_with_individual_rqst_errors.json'

        request.return_value = Mock()
        request.return_value.status_code = 200
        with open(os.path.join(FIXTURES, fixture), 'rb') as jsonfile:
            request.return_value.text = jsonfile.read()

        batch_requests = [
            {'method': 'GET', 'relative_url': 'kevin.r.stanton'},
            {'method': 'GET', 'relative_url': 'sproutsocialinc'}
        ]

        fbg = FBGraph('mocktoken')
        responses = fbg.batch(batch_requests)

        self.assertEquals(len(responses), 2)
        self.assertEquals(responses[0]['code'], 200)
        self.assertEquals(responses[0]['body']['id'], '537208670')
        self.assertEquals(responses[1]['code'], 400)
        self.assertDictEqual(responses[1]['body']['error'], {
            'code': 190,
            'type': 'OAuthException',
            'error_subcode': 460,
            'message': ('Error validating access token: The session has been ' +
                        'invalidated because the user has changed the password.')
        })

    @patch.object(requests, 'request')
    def test_request_hooks(self, request):
        request.return_value = Mock()
        request.return_value.status_code = 200
        request.return_value.text = '{}'

        pre_hook = Mock()
        post_hook = Mock()

        f = FBGraph(pre_hook=pre_hook, post_hook=post_hook)

        result = f.get('thing1')
        self.assertDictEqual(result, {})
        result = f.get('thing2')
        self.assertDictEqual(result, {})
        self.assertEquals(pre_hook.call_count, 2)
        self.assertEquals(post_hook.call_count, 2)
