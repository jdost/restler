import unittest
from restler import Restler, Route
import http_server

http_server.QUIET = True


class TestRestler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http_server.TestServer(port=9001, threaded=True)
        cls.server.start()

    def setUp(self):
        self.local = Restler("http://127.0.0.1:9001")

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_simple_request(self):
        ''' Test a basic request to the test server
        Just sends a basic request and makes sure the data is set to the
        defaults
        '''
        response = self.local()
        self.assertEquals(response.url, "http://127.0.0.1:9001/")
        self.assertEquals(response.data['method'], "GET")
        self.assertEquals(response.data['params'], {})

    def test_different_methods(self):
        ''' Test that various methods are used if dictated
        Makes requests with the common RESTful methods and makes sure the
        server sees them used.
        '''
        for method in ['GET', 'POST', 'PATCH', 'PUT', 'DELETE']:
            response = self.local(method=method)
            self.assertEquals(response.data['method'], method)

    def test_long_routes(self):
        ''' Test that making a long path successfully sends to the server
        Makes a request using a long path and ensures that this is the path
        that the end server sees.
        '''
        response = self.local.a.long.route.making.a.request()
        self.assertEquals(
            str(response.data['path']),
            "http://127.0.0.1:9001/a/long/route/making/a/request")
        self.assertIsInstance(response.data['path'], Route)

    def test_params(self):
        ''' Test that params go through
        Sends a variety of types to the test server and sees if they are
        received correctly.
        '''
        response = self.local(foo="bar", bar=1, baz=True)
        try:
            self.assertItemsEqual(response.data['params'],
                                  {"foo": "bar", "bar": 1, "baz": True})
        except AttributeError:
            self.assertDictEqual(response.data['params'],
                                 {"foo": "bar", "bar": "1", "baz": "True"})
