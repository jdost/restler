import re
from datetime import datetime
from restler.utils import isstr
from collections import namedtuple

DateFormat = namedtuple("DateFormat", ['matcher', 'parser'])


class DateHandler(object):
    """ Datetype handler for date and time strings.  Can be extended with
    various formats for string representations and will use the built in
    ``stptime`` function to generate the rich ``datetime`` object of the raw
    string value.
    """
    current = None
    types = []

    @classmethod
    def register(cls, regex, parse_str):
        """ Register a new regex based string and strptime string to use for
        detecting and parsing the raw data string into the rich ``datetime``
        object.
        """
        cls.types.append(DateFormat(matcher=re.compile(regex),
                                    parser=parse_str))

    @classmethod
    def detection(cls, response, value):
        """ Goes through registered string format types and provides whether
        any of them match the provided string value.  Keeps track of which
        format was matched so that it may later be used for conversion.
        """
        for dateset in cls.types:
            if not isstr(value):
                continue
            if dateset.matcher.match(value):
                cls.current = dateset.parser
                return True

        cls.current = None
        return False

    @classmethod
    def handler(cls, response, value):
        """ Converts the raw value into a rich ``datetime`` object using the
        most recently detected format as the parsing definition.
        """
        if not cls.current:
            return value

        new_date = datetime.strptime(value, cls.current)
        cls.current = None

        return new_date

DateHandler.register("[0-3][0-9]/[0-3][0-9]/[0-9]{2}", "%m/%d/%y")

from restler import Response
Response.add_datatype(DateHandler.detection, DateHandler.handler)
