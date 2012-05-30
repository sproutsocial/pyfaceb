import unittest
import requests
from pyfaceb import FBGraph
from mock import patch, Mock
from pyfaceb.exceptions import (FBJSONException, FBHTTPException,
                                FBConnectionException)
from requests.exceptions import SSLError

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
    def test_FBJSONException(self, request):
        mock_response = Mock()
        mock_response.text = 'i am bad json'
        mock_response.status_code = 200
        request.return_value = mock_response

        fbg = FBGraph()
        self.assertRaises(FBJSONException, fbg.get, ('me',))

    @patch.object(requests, 'request')
    def test_FBHTTPException(self, request):
        mock_response = Mock()
        mock_response.text = 'some fb error'
        mock_response.status_code = 400
        request.return_value = mock_response

        fbg = FBGraph()
        self.assertRaises(FBHTTPException, fbg.get, ('me',))
        try:
            data = fbg.get('me')
        except FBHTTPException as e:
            self.assertEquals(e.message, 'some fb error')

    @patch.object(requests, 'request')
    def test_FBConnectionException(self, request):
        def side_effect(*args, **kwargs):
            raise SSLError('The read operation timed out')
        request.side_effect = side_effect

        fbg = FBGraph()
        self.assertRaises(FBConnectionException, fbg.get, ('me',))
        self.assertRaises(FBConnectionException, fbg.post,
            ('me', '', {'junk': 'data'}))

