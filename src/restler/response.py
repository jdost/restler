try:
    import httplib
except ImportError:
    import http.client as httplib

from restler.utils import isstr, cstrip
from restler.errors import ServerError, RequestError
from collections import namedtuple


DatatypeHandler = namedtuple("DatatypeHandler", ['detector', 'handler'])


class Response(object):
    """ Base Response handler/wrapper that attempts to normalize and parse the
    HTTP response body.  Attempts to handle parsing the data structure based on
    MIMEtype, types of the parsed structure, and provide pythonic interfaces to
    the underlying logic (i.e. bad requests evaluate as False when treated as a
    boolean, etc).
    """
    datatypes = []
    mimetypes = {}

    def __init__(self, response, base):
        self.__base__ = response
        self.__parent__ = base
        self.url = self.__base__.geturl()
        self.headers = self.__base__.info()
        self.data = ""
        self.code = response.getcode()
        self.link = None

        if self.code >= httplib.INTERNAL_SERVER_ERROR:
            raise ServerError(self.code, self.__base__.read())
        elif self.code >= httplib.BAD_REQUEST:
            raise RequestError(self.code, self.__base__.read())

        self.convert()
        self.data = self.parse(self.data)
        self.parse_headers()

    @classmethod
    def add_datatype(cls, datatype, handler):
        """ Register a new datatype handler for :class:`Response <Response>`
        parsing.  Takes two functions, a detection function that will be used
        to detect if the raw response value is viable to be handled, and a
        handling function which, if the detection is valid, will convert the
        raw response data into the rich datatype.

        :param function datatype: returns a boolean on whether the passed in
            data is handleable, the signature is `handler(response, value)`
        :param function handler: returns the parsed output of the raw input as
            handled by the handling function, it has the same signature as the
            handler

        For examples on use, look at :module:`DateHandler <date_handler>` or
        :module:`URLHandler <url_handler>`.
        """
        cls.datatypes.append(DatatypeHandler(detector=datatype,
                                             handler=handler))

    @classmethod
    def add_mimetype(cls, mime, handler):
        """ Register a new mimetype handler to handle converting the raw data
        string into the represented rich data structure.  Relies entirely on
        the response's reported content type to register the handling function.

        :param str mime: Raw MIMEtype string expected in the response header
        :param function handler: handling function that will return the
            structured data representation based on the passed in raw response
            body

        For examples on use, look at :module:`JSONHandler <json_handler>` or
        :module:`FormHandler <form_handler>`
        """
        cls.mimetypes[mime] = handler

    def convert(self):
        """ Goes through registered MIMEtype strings and attempts to convert
        the raw response body into the structured data based on the handlers
        registered.
        """
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
        """ Traverses the data structure and converts any data of a base type
        into a richer form based on registered detection functions and the
        corresponding handling function.

        Provided handlers include a URL detector that will convert the URL
        string into a :class:`Route <Route>` if applicable and a date detector
        that will convert a string like ``2013-03-12`` into the rich
        ``datetime`` object.
        """
        # handle is just a function that is mapped against a list
        def handle(val):
            for datatype in self.datatypes:
                if datatype.detector(self, val):
                    return datatype.handler(self, val)

            return val

        if isinstance(data, list):
            return list(map(self.parse, data))
        elif not isinstance(data, dict):
            return handle(data)

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self.parse(value)
                continue

            if isinstance(value, list):
                data[key] = map(self.parse, value)

            if not isstr(value):
                continue

            data[key] = handle(value)

        return data

    def parse_headers(self):
        """ Goes through the list of headers on the response and converts known
        headers using defined handlers.
        """
        if 'Link' in self.headers:
            self.__link_header()

    def __link_header(self):
        links_raw = self.__base__.headers['Link'].split(',')
        links = {}
        for link in links_raw:
            info = Links.parse(link)
            links[info['rel']] = info["url"]

        self.links = Links(self.__parent__, links)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]

        if self.data and isinstance(self.data, dict):
            return self.data[attr]

        raise KeyError(attr)

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __repr__(self):
        return "<Response: {!s}>".format(self.url)

    def __str__(self):
        return self.__base__.read()

    def __nonzero__(self):
        return self.code < httplib.BAD_REQUEST


class Links(object):
    """ Rich representation of the ``Link`` Header field.
    """
    def __init__(self, parent, links):
        self.parent = parent
        self.links = links

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]

        if attr in self.links:
            url = self.links[attr]

            return self.parent[url]

        return None

    def __getitem__(self, item):
        return self.__getattr__(item)

    @classmethod
    def parse(cls, raw):
        info_raw = raw.split(';')
        info = {'url': info_raw[0].strip(' <>"')}
        for i in info_raw[1:]:
            key, value = cstrip(i, " \"'").split("=", 1)
            info[key] = value

        return info
