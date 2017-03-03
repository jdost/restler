import json


def handler(response, body):
    """ MIMEtype handling function for JSON data strings.  Performs the
    conversion fromt he raw JSON string into the rich JSON structure using the
    built in ``json`` library.
    """
    return json.loads(body)

from restler import Response
Response.add_mimetype("application/json", handler)
