import unittest
from restler import Restler, Route, Response, RequestError, ServerError
import json


class TestResponse(unittest.TestCase):
    def setUp(self):
        self.app = Restler("http://nope/")
# Mimetypes

    def test_json(self):
        ''' Tests that the `Content-Type` for json is identified and parsed
        This tests the __json_handler for mimetypes in `Response`
        '''
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, "{\"foo\":\"bar\"}")
        response = Response(r, self.app)

        self.assertTrue(isinstance(response.data, dict))
        self.assertTrue("foo" in response.data)
        self.assertEqual(response.data["foo"], "bar")

    def test_encoded(self):
        ''' Tests that the `Content-Type` for url encoded works
        This tests the __form_handler for mimetypes in `Response`
        '''
        r = ResponseTest(
            200,
            {"Content-Type": "application/x-www-form-urlencoded"},
            "foo=bar&bar=baz")
        response = Response(r, self.app)

        self.assertTrue(isinstance(response.data, dict))
        self.assertTrue("foo" in response.data)
        self.assertEqual(response.data["foo"], "bar")
# URL datatypes

    def test_URLs(self):
        ''' Test that the URL special datatype handler works
        Tests the special handler for URL datatypes gets identified and used
        '''
        params = {"url": "/test"}
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, json.dumps(params))
        response = Response(r, self.app)

        self.assertEqual(response.data["url"], "http://nope/test/")

    def test_fullURLs(self):
        ''' Test that full URLs are handled
        Tests the handler for full URLs (ones including the host) are
        caught and properly converted.
        '''
        params = {"url": "http://nope/test2"}
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, json.dumps(params))
        response = Response(r, self.app)

        self.assertTrue(isinstance(response.data["url"], Route))
        self.assertEqual(response.data["url"], "http://nope/test2/")

    def test_nonroot_URLs(self):
        ''' Test that URLs of a non root base URL are handled properly
        This is a test for when an app uses a path in the base URL (i.e.
        something like `http://twitter.com/api/`) so URLs that get converted
        take into account this additional base folder
        '''
        self.app = Restler("http://nope/test/")
        params = {"url": "/test"}
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, json.dumps(params))
        response = Response(r, self.app)

        self.assertEqual(response.data["url"], "http://nope/test/")
    # Bug, url in above doesn't have trailing slash, messed up with the natural
    # trailing slash
        self.app = Restler("http://nope/test/")
        params = {"url": "/test/"}
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, json.dumps(params))
        response = Response(r, self.app)

        self.assertEqual(response.data["url"], "http://nope/test/")

    def test_nonroot_mismatchURLs(self):
        ''' Tests that URLs of a non root base URL handle mismatches
        This is when the passed in URL is for a root folder that is not the
        same as the base subfolder of the application.
        '''
        self.app = Restler("http://nope/test/")
        params = {"url": "/derp"}
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, json.dumps(params))
        response = Response(r, self.app)

        self.assertEqual(response.data["url"], "/derp")

    def test_url_bad_types(self):
        ''' Tests that url handler doesn't break on non strings
        Tests various types other than strings being passed into the url
        handler and it doesn't fall over.
        '''
        types = [
            15,
            True,
            None,
            1.5,
        ]

        for t in types:
            params = {"url": t}
            ResponseTest(
                200, {"Content-Type": "application/json"}, json.dumps(params))
# datetime datatypes

    def test_date(self):
        ''' Tests that datetime strings are handled as datetimes
        Tests the various formats for datetime strings and makes sure they get
        converted into the proper structure.
        '''
        params = {"date": "12/24/99"}
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, json.dumps(params))
        response = Response(r, self.app)

        self.assertEqual(response.data["date"].strftime("%Y%m%d"), "19991224")

    def test_date_bad_types(self):
        ''' Tests that datetime doesn't break on non strings
        Tests various types other than strings being passed into the datetime
        handler and it doesn't fall over.
        '''
        types = [
            15,
            True,
            None,
            1.5,
        ]

        for t in types:
            params = {"date": t}
            ResponseTest(
                200, {"Content-Type": "application/json"}, json.dumps(params))

    def test_errors(self):
        ''' Tests that errors are raised for status codes
        Errors should be raised for URL error responses (4xx and 5xx)
        '''
        r = ResponseTest(400, {}, "Bad Request")
        with self.assertRaises(RequestError) as err:
            Response(r, self.app)

        self.assertEqual(str(err.exception), "Bad Request")

        r = ResponseTest(500, {}, "Server Error")
        with self.assertRaises(ServerError) as err:
            Response(r, self.app)

        self.assertEqual(str(err.exception), "Server Error")

# Helper classes


class HeadersTest(dict):
    ''' Extended `dict` to mimic the Headers object of a Response '''
    def gettype(self):
        return self.get("Content-Type", "")


class ResponseTest(object):
    ''' Object meant to mimic a response object from `urllib2.urlopen` '''
    def __init__(self, code, headers, data, url=''):
        self.__url = url
        self.__data = data
        self.__code = code
        self.__headers = HeadersTest(headers)

    def getcode(self):
        ''' Status code getter '''
        return self.__code

    def read(self):
        ''' Body reader, file-like object '''
        return self.__data

    def info(self):
        ''' Headers getter '''
        return self.__headers

    def geturl(self):
        ''' URL getter '''
        return self.__url
