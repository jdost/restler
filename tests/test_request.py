import unittest
import json
from restler import Restler


def normalize(s):
    return s.decode("utf8") if isinstance(s, bytearray) else s


class TestRequest(unittest.TestCase):
    def setUp(self):
        self.app = Restler("http://127.0.0.1/")
        self.app.__test__ = True

    def assertSameUrlStrings(self, a, b):
        a_set = a.split("&")
        b_set = b.split("&")
        if hasattr(self, "assertItemsEqual"):
            return self.assertItemsEqual(a_set, b_set)
        else:
            return self.assertCountEqual(a_set, b_set)

    def test_basic(self):
        ''' Tests the basic Request formation from a `Route`
        Gets the created `urllib2.Request` object and confirms basic setup
        '''
        request = self.app.users()
        self.assertEqual(request.get_selector(), "/users")

    def test_methods(self):
        ''' Tests the method and data setup for a `Request`
        Checks the created Request object for method setup and data creation
        '''
        request = self.app.users("POST", user="test")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(normalize(request.get_data()), "user=test")

    def test_method_casing(self):
        ''' Tests the casing of the method
        Makes sure the method gets cast to all uppercase
        '''
        request = self.app.users("post")
        self.assertEqual(request.get_method(), "POST")

    def test_headers(self):
        ''' Tests setting a header for a request
        Checks that you can set headers via the request call
        '''
        request = self.app.users(headers={"Accepts": "application/json"})
        self.assertTrue(request.has_header("Accepts"))

    def test_json(self):
        ''' Tests the data body respects the content-type
        Sets the `Content-type` header for json, the data body should use this
        mimetype
        '''
        request = self.app.users(headers={"Content-type": "application/json"},
                                 users="test", foo="bar")
        self.assertEqual(json.dumps({"users": "test", "foo": "bar"}),
                         normalize(request.get_data()))

    def test_long_data(self):
        ''' Tests the data body for lots of data
        Creates a request with a large set of data, checks that it all gets
        added to the data body
        '''
        request = self.app.users(users="test", foo="bar", bar="baz")
        self.assertSameUrlStrings("foo=bar&bar=baz&users=test",
                                  normalize(request.get_data()))

    def test_qs_path(self):
        ''' Tests that a path with a query string sets the params
        If a path with a query string is fed into a `Route`, the query string
        should be parsed and set as default params
        '''
        route = self.app['users?name=test']
        request = route("POST")
        self.assertEqual("name=test", normalize(request.get_data()))
        self.assertEqual(request.get_selector(), "/users")

    def test_multi_params(self):
        ''' Tests a data body with an array value
        Creates a request with multiple values for a key set, checks that the
        key is used for each value individually.
        '''
        request = self.app.users(users=["foo", "bar", "baz"])
        self.assertSameUrlStrings("users=foo&users=bar&users=baz",
                                  normalize(request.get_data()))

    def test_get_data(self):
        ''' Tests that data for a GET is in the query string
        The data will also be in the header, but it is common for the data to
        live in the query string of the URL.
        '''
        route = self.app.test
        request = route(foo="bar")
        self.assertEqual("foo=bar", normalize(request.get_data()))
        self.assertEqual("/test?foo=bar", normalize(request.get_selector()))

    def test_reusable_routes(self):
        ''' Tests that the route builder re-uses routes of the same path
        The route builder should not need to build a new route for every hop in
        the path and should be able to re-use routes that have been created for
        a path.
        '''
        route = self.app.reusable
        route.params.add_params(foo="bar")
        self.assertDictEqual(self.app.reusable.params._default_params,
                             {"foo": "bar"})
