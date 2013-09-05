import unittest
from restler import Restler


class TestBasic(unittest.TestCase):
    def setUp(self):
        self.app = Restler("http://127.0.0.1:9001")

    def test_root(self):
        ''' Tests that the base app gets properly set
        Tests the basic values of the application object get properly set
        '''
        self.assertEqual(self.app, "http://127.0.0.1:9001")

    def test_path_building(self):
        ''' Tests that the path building works
        Tests the ability for the wildcard attribute handling gets properly
        used and the resulting `Route` object is correct.
        '''
        self.assertEqual(
            self.app.users, "http://127.0.0.1:9001/users/")
        self.assertEqual(
            self.app.users.info, "http://127.0.0.1:9001/users/info/")

    def test_deep_path(self):
        ''' Tests the path building works for large paths
        Stress test, ensures that long paths get properly handled (i.e.
        chaining)
        '''
        self.assertEqual(
            self.app["users/test/whoa/deep"],
            "http://127.0.0.1:9001/users/test/whoa/deep/")
        self.assertEqual(
            self.app.users.test.whoa.deep,
            "http://127.0.0.1:9001/users/test/whoa/deep/")

    def test_comparison(self):
        ''' Tests the comparison operators for `Route` '''
        test = self.app.users
        self.assertEqual(test, self.app.users)
        self.assertNotEqual(test, self.app.user)

    def test_attribute_path(self):
        ''' Tests the key based attribute conversion
        This is a test for the keybased (['key'] versus `.key`) access, this
        is for the ability to pass in opaque strings and have them get
        converted into the proper `Route` object.
        '''
        test = self.app.users.test
        self.assertEqual(test, self.app.users["test"])
        self.assertEqual(test["1234"], self.app.users["test"]["1234"])

    def test_root_path(self):
        ''' Tests the key based attribute conversion with root URLs
        Tests the key based access with root URLs (i.e. those starting with a
        slash)
        '''
        test = self.app.users.test
        self.assertEqual(test, test["/users/test"])
