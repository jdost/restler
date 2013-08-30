import unittest
from restler import Restler


class TestRequest(unittest.TestCase):
    def setUp(self):
        self.app = Restler("http://127.0.0.1/")
        self.app.__test__ = True

    def test_basic(self):
        request = self.app.users()
        self.assertEqual(request.get_selector(), "/users/")

    def test_methods(self):
        request = self.app.users("POST", user="test")
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_data(), "user=test")

    def test_method_casing(self):
        request = self.app.users("post")
        self.assertEqual(request.get_method(), "POST")

    def test_headers(self):
        request = self.app.users(headers={"Accepts": "application/json"})
        self.assertTrue(request.has_header("Accepts"))
