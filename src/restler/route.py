try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
    from functools import reduce

from restler.response import Response
from restler.utils import isstr, to_urlstr
from restler.errors import ERRORS, InvalidURLError, ServerError, RequestError
import json


class Route(object):
    ''' Route:
    The `Route` object is a wrapper around requests to a URL it is attached to
    (passed in upon construction) usually via the attribute based URL building
    from it's parent `Route` object.
    '''
    _default_params = {}
    _default_headers = []
    TRAILING_SLASH = False

    def __init__(self, url, base, default="GET"):
        ''' (constructor):
        '''
        self._default_params = Route._default_params.copy()
        if url.query:
            self.add_params(**url.query)

        self.__path__ = url
        self.__base = base
        self.__response_class = Response
        self.default_method = default

    def add_params(self, **params):
        ''' add_params:
        Takes key=value pairs of parameters to add to the default call params
        '''
        self._default_params.update(params)

    def __call__(self, method=None, *args, **kwargs):
        ''' __call__:
        Makes a request to the URL attached to this `Route` object.  If there
        is a `method` argument set, it will be used as the method, otherwise
        the default method (set on creation) will be used (defaults to `GET`).
        '''
        method = method if isinstance(method, str) else self.default_method
        return self.__request__(method=method, *args, **kwargs)

    def __request__(self, method, headers={}, *args, **kwargs):
        ''' __request__:
        Base request method, actually performs the request on the URL with the
        defined method.
        '''
        headers = dict(self._default_headers + list(headers.items()))

        params = dict(list(self._default_params.items()) +
                      list(kwargs.items()))
        if len(params):
            default_MIME = "application/x-www-form-urlencoded"
            if headers.setdefault("Content-type", default_MIME) == \
                    default_MIME:
                params = to_urlstr(params)
            elif headers["Content-type"] == "application/json":
                params = json.dumps(params)
            else:
                pass  # No idea what mimetype to encode against
        else:
            params = ""
            if len(args) > 0 and isstr(args[0]):
                params = args[0]
                headers.setdefault("Content-type", "text/plain")

        # Use the query string for GET ?
        if method.upper() == 'GET' and len(params):
            request = urllib2.Request(
                "?".join([str(self), params]),
                data=bytearray(params, 'utf-8'), headers=headers)
        else:
            request = urllib2.Request(
                str(self), data=bytearray(params, 'utf-8'),
                headers=headers)

        request.get_method = lambda: method.upper()

        if self.__base.__test__:
            return request

        try:
            response = self.__base.__opener__.open(request)
            return self.__response__(response)
        except urllib2.URLError:
            if self.__base__.EXCEPTION_THROWING:
                raise InvalidURLError(str(self))
            else:
                return (ERRORS["InvalidURL"], None)

    def __response__(self, response):
        ''' __response__:
        Handles the response body from a request.  This, by default, just lets
        the `Response` object do the main parsing and returns the object.
        '''
        try:
            response = self.__response_class(response, self.__base)
            if not self.__base.EXCEPTION_THROWING:
                return 0, response
            return response
        except ServerError as err:
            if self.__base.EXCEPTION_THROWING:
                raise err
            else:
                return (ERRORS["ServerError"], err)
        except RequestError as err:
            if self.__base.EXCEPTION_THROWING:
                raise err
            else:
                return (ERRORS["RequestError"], err)

    @classmethod
    def copy(cls):
        class RouteClone(cls):
            _default_params = {}
            _default_headers = []
            TRAILING_SLASH = False

        return RouteClone

    def __getattr__(self, attr):
        ''' __getattr__:
        Retrieves the existing method from the `Route` object, if it does not
        exist, creates a descendent Route with the attribute name as the new
        level in the URL.

        ex.
        >> users
        'Route: http://myweb.app/users/'
        >> users.test
        'Route: http://myweb.app/users/test/'
        '''
        if attr in self.__dict__:
            return self.__dict__[attr]

        if attr.startswith('/'):
            return self.__base[attr]

        return self.__base.__get_path__(self.__path__ + attr)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __repr__(self):
        return 'Route: {!s}'.format(self.__path__)

    def __str__(self):
        return str(self.__path__)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __hash__(self):
        return reduce(lambda s, x: s ^ ord(x), str(self), 0)


class Builder(object):
    def __init__(self, base, build_class=Route):
        self.lookup = {}
        self._build_class = build_class
        self.base = base

    def __call__(self, url, query=None):
        current_lookup = self.lookup
        for level in url.path:
            current_lookup = current_lookup.setdefault(level, {})

        route = current_lookup.get("__route__")
        if not route:
            route = self._build_class(url, self.base)
            current_lookup["__route__"] = route

        if url.query:
            route.add_params(**url.query)
        if query:
            route.add_params(**query)

        return route
