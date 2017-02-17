try:
    import urllib2
    import cookielib
except ImportError:
    import urllib.request as urllib2
    import http.cookiejar as cookielib


class Cookies(object):
    def __init__(self, jar, url):
        self.url = url
        if isinstance(jar, cookielib.CookieJar):
            self.jar = jar
        elif isinstance(jar, cookielib.CookiePolicy):
            self.jar = cookielib.CookieJar(policy=jar)
        else:
            self.jar = cookielib.CookieJar()

    @property
    def handler(self):
        return urllib2.HTTPCookieProcessor(self.jar)
