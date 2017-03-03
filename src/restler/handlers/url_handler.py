from restler.utils import isstr


class URLHandler(object):
    """ Datatype handler for URL strings.  Attempts to detect whether the
    string respresents a valid URL within the namespace of the base URL
    definition and converts the value into an equivalent :class:`Route <Route>`
    """

    @classmethod
    def detection(cls, response, value):
        """ Tests if the value matches a format that signifies it is either an
        absolute or relative path.
        """
        if not isstr(value):
            return False

        return value.startswith('/') or \
            value.startswith(str(response.__parent__))

    @classmethod
    def handler(cls, response, value):
        """ Generates a representative :class:`Route <Route>`
        """
        return response.__parent__[value]

from restler import Response
Response.add_datatype(URLHandler.detection, URLHandler.handler)
