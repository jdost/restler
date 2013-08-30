import unittest
from restler import Restler


class TestBasic(unittest.TestCase):
    def setUp(self):
        self.app = Restler("http://127.0.0.1:9001")

    def test_root(self):
        self.assertEqual(self.app, "http://127.0.0.1:9001")

    def test_path_building(self):
        self.assertEqual(
            self.app.users, "http://127.0.0.1:9001/users/")
        self.assertEqual(
            self.app.users.info, "http://127.0.0.1:9001/users/info/")

    def test_deep_path(self):
        self.assertEqual(
            self.app["users/test/whoa/deep"],
            "http://127.0.0.1:9001/users/test/whoa/deep/")

    def test_comparison(self):
        test = self.app.users
        self.assertEqual(test, self.app.users)
        self.assertNotEqual(test, self.app.user)

    def test_attribute_path(self):
        test = self.app.users.test
        self.assertEqual(test, self.app.users["test"])
        self.assertEqual(test["1234"], self.app.users["test"]["1234"])

    def test_root_path(self):
        test = self.app.users.test
        self.assertEqual(test, test["/users/test"])
