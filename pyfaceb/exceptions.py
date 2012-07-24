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
    """
    def __init__(self, code, body):
        self.code = code
        self.body = body

        # for backwards compatibility
        self.message = body

    def __repr__(self):
        values = (self.__class__.__name__, self.code, self.body)
        return '%s(%s, \'%s\')' % values

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