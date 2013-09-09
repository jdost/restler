try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode
try:
    import httplib
except ImportError:
    import http.client as httplib
try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs

__version__ = '0.2'


def isstr(s):
    try:
        return isinstance(s, str) or isinstance(s, unicode)
    except NameError:
        return isinstance(s, str)


class Restler(object):
    ''' Restler:
    RESTler is a wrapper around a web app API.  It sets the base URL and allows
    for attribute/OO based access to the RESTful URLs.

    ex.
    >> github = Restler('http://api.github.com/')
    >> github
    'Restler: http://api.github.com/'
    >> github.user
    'Route: http://api.github.com/user/'
    >> github.user.username
    'Route: http://api.github.com/user/username/'
    '''
    __name__ = "Restler v{}".format(__version__)

    def __init__(self, base, cookies=False):
        ''' (constructor):
        '''
        self.EXCEPTION_THROWING = True  # set to False if you want return codes
        self.__test__ = False

        url_info = urlparse(base)
        scheme = url_info.scheme if len(url_info.scheme) else 'http'
        self.__url__ = '{}://{}'.format(scheme, url_info.netloc)
        self.__route_class = Route
        self.__route = self.__route_class(url_info.path, self)

        self.__opener__ = urllib2.build_opener()
        self.__opener__.addheaders = [('User-agent', self.__name__)]

        if cookies:  # `cookies` can be a bool, the CookieJar or CookiePolicy
            import cookielib
            if isinstance(cookies, cookielib.CookieJar):
                cj = cookies
            elif isinstance(cookies, cookielib.CookiePolicy):
                cj = cookielib.CookieJar(policy=cookies)
            else:
                cj = cookielib.CookieJar()

            self.__opener__.add_handler(urllib2.HTTPCookieProcessor(cj))

    def __call__(self, *args, **kwargs):
        ''' __call__:
        Acts as a call to the base URL `Route` for the application.
        '''
        return self.__route(*args, **kwargs)

    def __getattr__(self, attr):
        ''' __getattr__:
        Retrieves the existing method from the `Restler` object, if it does not
        exist, passes the attribute to the base route, returning any of it's
        existing methods or creates a child `Route` object for the new URL.

        Note: due to the existing method lookup, if your web API has a route
        for '[base URL]/base/', '[base URL]/base_class/', etc, they will not
        map properly as those are defined properties
        '''
        if attr in self.__dict__:
            return self.__dict__[attr]

        if attr.startswith('/'):
            if len(self.__route.__path__) > 0:
                if not attr.startswith(self.__route.__path__.rstrip('/')):
                    return attr
                attr = attr[len(self.__route.__path__):]

        return self.__route.__getattr__(attr.lstrip('/'))

    def __getitem__(self, attr):
        return self.__getattr__(attr)

    def __repr__(self):
        return 'Restler: ' + str(self.__url__)

    def __str__(self):
        return str(self.__url__)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __hash__(self):
        return reduce(lambda s, x: s ^ ord(x), str(self), 0)


class Route(object):
    ''' Route:
    The `Route` object is a wrapper around requests to a URL it is attached to
    (passed in upon construction) usually via the attribute based URL building
    from it's parent `Route` object.
    '''
    _default_params = {}
    _default_headers = []

    def __init__(self, path, base, default="GET"):
        ''' (constructor):
        '''
        if path.find("?") != -1:
            path, qs = path.split("?", 1)
            qs = parse_qs(qs)
            for key, value in qs.items():
                if len(value) == 1:
                    qs[key] = value[0]
            self._default_params = dict(list(self._default_params.items()) +
                                        list(qs.items()))

        if not path.endswith('/'):
            path += '/'

        self.__path__ = path
        self.__base = base
        self.__response_class = Response
        self.default_method = default

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
                params = urlencode(params)
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
                raise InvalidURLError()
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

        attr = attr.rstrip("/")

        if attr.find("/") > 0:
            path, remainder = attr.split("/", 1)
            return self.__class__(''.join([self.__path__, path]),
                                  self.__base)[remainder]

        return self.__class__(''.join([self.__path__, attr]), self.__base)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __repr__(self):
        return 'Route: ' + ''.join([self.__base.__url__, self.__path__])

    def __str__(self):
        return ''.join([self.__base.__url__, self.__path__])

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __hash__(self):
        return reduce(lambda s, x: s ^ ord(x), str(self), 0)


class Response(object):
    ''' Response:
    The `Response` object is a handler+wrapper for the response document from
    the HTTP requests.  It handles trying to parse the string of data into a
    proper data structure, interpreting the status code, and organizing all of
    the information into a manageable format.
    '''
    datatypes = []
    mimetypes = {}

    def __init__(self, response, base):
        self.__base__ = response
        self.__parent__ = base
        self.url = self.__base__.geturl()
        self.headers = self.__base__.info()
        self.data = ""
        self.code = response.getcode()

        if self.code >= httplib.INTERNAL_SERVER_ERROR:
            raise ServerError(self.code, self.__base__.read())
        elif self.code >= httplib.BAD_REQUEST:
            raise RequestError(self.code, self.__base__.read())

        self.convert()
        self.data = self.parse(self.data)
        self.parse_headers()

    @classmethod
    def add_datatype(cls, datatype, handler):
        ''' (class) add_datatype:
        Takes a datatype detection function and handler function and adds it to
        the set of handlers for the various custom datatypes evaluated after
        conversion via mimetype.  The detection function takes two arguments,
        the first is the actual `Response` object (the functions are treated
        as methods of the object) and the second is the raw value (only strings
        are passed in).  The second function also takes two arguments, the
        first, again, being the `Response` object and the second being the
        value that was previously detected against.  Whatever it returns will
        be used instead of this value.
        '''
        cls.datatypes.append([datatype, handler])

    @classmethod
    def add_mimetype(cls, mime, handler):
        ''' (class) add_mimetype:
        Takes a `MIMEtype` string and a handler function and adds it to the
        lookup set for response handling.  The passed in function will take
        two parameters, the first is the actual `Response` object (the
        functions are treated as methods of the object) and the second is the
        raw body of the response.
        '''
        cls.mimetypes[mime] = handler

    def convert(self):
        ''' convert:
        Attempts to detect the MIMEtype of the response body and convert
        accordingly.
        '''
        try:
            mime = self.__base__.info().gettype()
        except AttributeError:
            mime = self.__base__.info().get_content_type()
        for mimetype, handler in self.mimetypes.items():
            if mimetype == mime:
                raw = self.__base__.read()
                if isinstance(raw, bytes):
                    raw = raw.decode("UTF-8")
                self.data = handler(self, raw)
                return

        self.data = self.__base__.read()

    def parse(self, data):
        ''' parse:
        Loops over the data, looking for string values that can be parsed into
        rich data structures (think 2012-12-24 becomes a `datetime` object).
        '''
        # handle is just a function that is mapped against a list
        def handle(val):
            for datatype in self.datatypes:
                if datatype[0](self, val):
                    return datatype[1](self, val)

            return val

        if isinstance(data, list):
            return list(map(handle, data))
        elif not isinstance(data, dict):
            return data

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self.parse(value)
                continue

            if isinstance(value, list):
                data[key] = list(map(handle, value))

            if not isstr(value):
                continue

            data[key] = handle(value)

        return data

    def parse_headers(self):
        ''' parse_headers:
        Traverses the headers of the response and sets them in the `headers`
        dictionary of the object.  Any handlers set for a header type will be
        run against a header if it exists.
        '''
        if 'Link' in self.headers:
            self.__link_header()

    def __link_header(self):
        ''' (private) link_header:
        If the `Link` header is set in the response, the values will be parsed
        and appropriate methods will be added for the relative locations.
        '''
        links_raw = self.__base__.headers['Link'].split(',')
        links = {}
        for link in links_raw:
            info_raw = link.split(';')
            info = {'url': info_raw[0].strip(' <>')}
            for i in info_raw[1:]:
                i = i.split('=')
                info[i[0]] = i[1]

            links[info['rel']] = info

    def __repr__(self):
        return "Response: " + self.url

    def __str__(self):
        return self.__base__.read()

    def __nonzero__(self):
        return self.code < httplib.BAD_REQUEST


# Various custom handlers
import json


def __json_handler(response, body):
    ''' json_handler:
    Performs a conversion from the raw string into a dictionary using the built
    in JSON library.
    '''
    return json.loads(body)

Response.add_mimetype("application/json", __json_handler)


def __form_handler(response, body):
    ''' form_handler:
    Performs a conversion from the raw string into a dictionary using the built
    in urlparsing library.
    '''
    data = parse_qs(body)
    for key, value in data.items():
        if len(value) == 1:
            data[key] = value[0]

    return data

Response.add_mimetype("application/x-www-form-urlencoded", __form_handler)


import re
from datetime import datetime


class __DateHandler(object):
    current = None
    types = [
        {"regex": "[0-3][0-9]/[0-3][0-9]/[0-9]{2}", "parse": "%m/%d/%y"}
    ]

    @classmethod
    def detection(cls, response, value):
        ''' DateHandler.detection:
        Tests if the value matches a recognized date string format (ISO, IETF,
        etc) so that it can then be converted into a more usable data
        structure.
        '''
        for dateset in cls.types:
            if re.match(dateset["regex"], value):
                cls.current = dateset["parse"]
                return True

        cls.current = None
        return False

    @classmethod
    def handler(cls, response, value):
        ''' DateHandler.handler:
        If the detection function found that the value was a date, the
        handler will be run against it.  As the detection already determined
        the parse string to use, this just needs to handle the conversion.
        '''
        if not cls.current:
            return value

        new_date = datetime.strptime(value, cls.current)
        cls.current = None

        #new_date.__str__ = lambda: value
        return new_date

Response.add_datatype(__DateHandler.detection, __DateHandler.handler)


class __URLHandler(object):
    @classmethod
    def detection(cls, response, value):
        ''' URLHandler.detection:
        Tests if the value matches a format that signifies it is either an
        absolute or relative path.
        '''
        return value.startswith('/') or \
            value.startswith(str(response.__parent__))

    @classmethod
    def handler(cls, response, value):
        ''' URLHandler.handler:
        Returns a `Route` object for the value.
        '''
        if value.startswith(str(response.__parent__)):
            value = value[len(str(response.__parent__)):]
        return response.__parent__[value]

Response.add_datatype(__URLHandler.detection, __URLHandler.handler)


# Exceptions/Errors
ERRORS = {
    'InvalidURL': 1,
    'RequestError': 4,  # 4xx errors
    'ServerError': 5    # 5xx errors
}


class InvalidURLError(Exception):
    pass


class RequestError(Exception):
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
    def __init__(self, code, body):
        self.code = code
        self.body = body

    def __cmp__(self, other):
        if self.code == other:
            return 0
        return 1 if self.code > other else -1

    def __str__(self):
        return self.body
