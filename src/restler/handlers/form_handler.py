try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs


def handler(response, body):
    """ MIMEtype handling function for form urlencoded data strings.  Performs
    the conversion from the raw url encoded string using the ``urlparse``
    library to handle the basic parsing.  (HTTP allows for the same key to be
    used multiple times, as this behaviour is often handled differently
    between applications, this does not attempt to handle these and it should
    be defined by the user based on the application being communicated with)
    """
    data = parse_qs(body)
    for key, value in data.items():
        if len(value) == 1:
            data[key] = value[0]

    return data

from restler import Response
Response.add_mimetype("application/x-www-form-urlencoded", handler)
