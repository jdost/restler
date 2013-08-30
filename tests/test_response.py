import unittest
from restler import Restler, Response
import json


class TestResponse(unittest.TestCase):
    def setUp(self):
        self.app = Restler("http://nope/")

    def test_json(self):
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, "{\"foo\":\"bar\"}")
        response = Response(r, self.app)

        self.assertTrue(isinstance(response.data, dict))
        self.assertTrue("foo" in response.data)
        self.assertEqual(response.data["foo"], "bar")

    def test_encoded(self):
        r = ResponseTest(
            200,
            {"Content-Type": "application/x-www-form-urlencoded"},
            "foo=bar&bar=baz")
        response = Response(r, self.app)

        self.assertTrue(isinstance(response.data, dict))
        self.assertTrue("foo" in response.data)
        self.assertEqual(response.data["foo"], "bar")

    def test_URLs(self):
        params = {"url": "/test"}
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, json.dumps(params))
        response = Response(r, self.app)

        self.assertEqual(response.data["url"], "http://nope/test/")

    def test_date(self):
        params = {"date": "12/24/99"}
        r = ResponseTest(
            200, {"Content-Type": "application/json"}, json.dumps(params))
        response = Response(r, self.app)

        self.assertEqual(response.data["date"].strftime("%Y%m%d"), "19991224")


class HeadersTest(object):
    def __init__(self, d):
        self.d = d

    def gettype(self):
        return self.d.get("Content-Type", "")


class ResponseTest(object):
    def __init__(self, code, headers, data):
        self.__data = data
        self.__code = code
        self.__headers = HeadersTest(headers)

    def getcode(self):
        return self.__code

    def read(self):
        return self.__data

    def info(self):
        return self.__headers
