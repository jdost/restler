# Exceptions/Errors
ERRORS = {
    'InvalidURL': 1,
    'RequestError': 4,  # 4xx errors
    'ServerError': 5    # 5xx errors
}


class InvalidURLError(Exception):
    """ Error raised when a URL is malformed or unparseable
    """
    pass


class RequestError(Exception):
    """ Error for when the request failed for a handled reason (4xx HTTP error
    codes)
    """
    def __init__(self, code, body):
        self.code = code
        self.body = body

    def __cmp__(self, other):
        if self.code == other:
            return 0
        return 1 if self.code > other else -1

    def __str__(self):
        return self.body


class ServerError(Exception):
    """ Error for when the request failed for an unhandled error on the server
    side (5xx HTTP error codes)
    """
    def __init__(self, code, body):
        self.code = code
        self.body = body

    def __cmp__(self, other):
        if self.code == other:
            return 0
        return 1 if self.code > other else -1

    def __str__(self):
        return self.body
