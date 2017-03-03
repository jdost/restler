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
    """ Base class responsible for wrapping the route definitions of a full URL
    that can be called/requested.

    These wrapped routes are generated via the dynamic attribute building of
    the core :class:`Restler <Restler>` class of the URL building.  ``Route``
    objects represent a full URL and when called will make a request to that
    location.

    Usage::

        >> users = github.users
        <Route: http://api.github.com/users/>
        >> user_list = users()
        <Response: http://api.github.com/users/>
        >> user_list.data
        { users: [ { username: "jdost" } ] }

    """
    _default_params = {}
    _default_headers = []
    TRAILING_SLASH = False

    def __init__(self, url, base, default="GET"):
        self._default_params = Route._default_params.copy()
        if url.query:
            self.add_params(**url.query)

        self.__path__ = url
        self.__base = base
        self.__response_class = Response
        self.default_method = default

    def add_params(self, **params):
        """ Add in key value pairs to the parameters used by default on
        requests.  The values will override existing ones if there are key
        collisions.
        """
        self._default_params.update(params)

    def __call__(self, method=None, *args, **kwargs):
        method = method if isinstance(method, str) else self.default_method
        return self.__request__(method=method, *args, **kwargs)

    def __request__(self, method, headers={}, *args, **kwargs):
        """ Makes a request to the represented URL of the object.  The method
        passed in will be used for the request and the rest of the arguments
        will be used to attempt to build the request body/data.
        """
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
        """ Response handler, takes a raw response body and attempts to build
        a :class:`Response <Response>` object with the returned data.
        """
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
        """ Builds a subpath :class:`Route <Route>` object using the attribute
        chain as the path to append to the current path.  If the attribute
        string corresponds to an existing attribute on the object, that will
        be given instead (This means that methods or attributes already set are
        illegal paths for the application).

        If you want to create a subpath that collides with an already defined
        attribute, you can use the `route['collision']` access pattern.

        Usage::

            >> users
            <Route: http://myweb.app/users/>
            >> users.test
            <Route: http://myweb.app/users/test/>

        """
        if attr in self.__dict__:
            return self.__dict__[attr]

        return self.__getitem__(attr)

    def __getitem__(self, item):
        if item.startswith('/'):
            return self.__base[item]

        return self.__base.__get_path__(self.__path__ + item)

    def __repr__(self):
        return '<Route: {!s}>'.format(self.__path__)

    def __str__(self):
        return str(self.__path__)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __hash__(self):
        return reduce(lambda s, x: s ^ ord(x), str(self), 0)


class Builder(object):
    """ Route building manager
    Calleable object that attempts to generate or re-use routes for new URLs
    to be generated.  Handles normalization of the URL, caches references to
    previously generated :class:`Route <Route>` objects, allowing for default
    overrides to carry forward to referencing the route again.
    """
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
