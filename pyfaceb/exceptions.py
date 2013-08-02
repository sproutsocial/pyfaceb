import json
import logging


W_JSON_PARSE = 'Unable to parse Facebook error json (Reason: %s)'

log = logging.getLogger(__name__)

class FBException(Exception):
    """
    Generic exception as a convenience to the client, if they don't care
    to handle different exception types differently.
    """
    pass

class FBHTTPException(FBException):
    """
    This exception is raised for HTTP errors encountered, i.e. a non-200 HTTP
    status codes.

    message: str, body of response
    body: str, body of response
    code: int, HTTP code
    json: deserialized json, will contain fallback error if unable to parse.
    """

    FALLBACK_ERROR_OBJ = {'error': {'message': 'Unknown error.',
                                    'type': 'Unknown',
                                    'code': None}}

    def __init__(self, code, body):
        self.code = code
        self.body = body

        try:
            self.json = json.loads(body)
        except ValueError as e:
            log.warn(W_JSON_PARSE, e.message)
            self.json = self.FALLBACK_ERROR_OBJ

        # for backwards compatibility
        self.message = body

    def __repr__(self):
        values = (self.__class__.__name__, self.code, self.body)
        return '%s(%s, %s)' % values

    def __str__(self):
        return self.__repr__()

class FBJSONException(FBException):
    """
    This exception is raised when the JSON response cannot be deserialized
    properly.
    """

class FBConnectionException(FBException):
    """
    This exception is raised for errors encountered at the connection level,
    like timeout errors, SSL errors, etc.
    """
    pass
