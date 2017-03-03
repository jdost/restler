try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs
from restler.utils import isstr


class URL(object):
    """ URL representation and manipulation structure, used for parsing,
    manipulating, and interacting with a rich URL string.  Handles parsing out
    protocol, domain, path, and query strings from a raw URL string.
    """
    PATH_DELIMITER = '/'
    QUERY_DELIMITER = '?'

    def __init__(self, base, path=None):
        if path is None:
            path = []
        url_info = urlparse(base)

        self.protocol = ""
        self.protocol = url_info.scheme if len(url_info.scheme) else 'http'
        if self.protocol is "unix":
            self.domain = "/" + url_info.path
            self.path, _ = URL.split(path)
        else:
            self.domain = url_info.netloc
            self.path = URL.split(url_info.path)[0] + path

        self.query = URL.translate_query(url_info.query)

    def __add__(self, path):
        return self.__extend__(path)

    def __div__(self, path):
        return self.__extend__(path)

    def __extend__(self, path):
        """ Generates a new :class:`URL <URL>` with the added path extended to
        the end of the existing path.  Can be triggered with the division and
        addition interaction methods.

        Usage::
            >> my_url
            URL<http://foo.bar/>
            >> my_url + "baz"
            URL<http://foo.bar/baz/>
            >> my_url / "back"
            URL<http://foo.bar/back/>

        """
        new_url = self.clone()

        path, query = URL.split(path)
        new_url.path += path
        new_url.query = dict(list(self.query.items()) + list(query.items)) \
            if query else self.query.copy()

        return new_url

    def clone(self):
        new_url = URL("{}://{}".format(self.protocol, self.domain), self.path)
        return new_url

    def __str__(self):
        return "{}://{}/{}".format(self.protocol, self.domain,
                                   "/".join(self.path))

    def __repr__(self):
        return "URL<{!s}>".format(self)

    @classmethod
    def split(cls, path):
        """ Break the path down into a list of the levels and the query string
        """
        query = None

        if isstr(path):
            url_info = urlparse(path)
            query = cls.translate_query(url_info.query)
            path = url_info.path.split(cls.PATH_DELIMITER)

        return list(filter(bool, path)), query

    @classmethod
    def translate_query(cls, qs):
        """ Translate and normalize a query string into a dictionary, makes
        some opinionated choices such as only taking the value if one value is
        reported (HTTP allows for multiple of the same key to be defined, and
        this does not attempt to normalize this scenario, it is on the user to
        define this behavior)
        """
        query = parse_qs(qs)
        query_dict = {}
        for key, value in query.items():
            if len(value) == 1:
                query_dict[key] = value[0]

        return query_dict
