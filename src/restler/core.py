try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
    from functools import reduce

from restler import __version__
from restler.route import Builder
from restler.url import URL, AuthManager, Cookies
from restler.utils import isstr


class Restler(object):
    ''' Restler:
    RESTler is a wrapper around a web app API.  It sets the base URL and allows
    for attribute/OO based access to the RESTful URLs.

    ex.
    >> github = Restler('http://api.github.com/')
    >> github
    'Restler: http://api.github.com/'
    >> github.user
    'Route: http://api.github.com/user/'
    >> github.user.username
    'Route: http://api.github.com/user/username/'
    '''
    __name__ = "Restler v{}".format(__version__)

    def __init__(self, base, cookies=False, follow_redirects=True,
                 http_auth=False):
        ''' (constructor):
        '''
        self.EXCEPTION_THROWING = True  # set to False if you want return codes
        self.__test__ = False

        self.__url__ = URL(base)
        self._route = Builder(self)
        self.__route = self._route(self.__url__)
        self.__auth_manager = None

        handlers = []
        if not follow_redirects:
            from restler.utils import NoRedirectHandler
            handlers.append(NoRedirectHandler)

        if cookies:  # `cookies` can be a bool, the CookieJar or CookiePolicy
            self.__cookie_manager = Cookies(cookies, self.__url__)
            handlers.append(self.__cookie_manager.handler)

        if http_auth:
            self.__auth_manager = AuthManager(http_auth, self.__url__)
            handlers.append(self.__auth_manager.handler)

        self.__opener__ = urllib2.build_opener(*handlers)
        self.__opener__.addheaders = [('User-agent', self.__name__)]

    def __call__(self, *args, **kwargs):
        ''' __call__:
        Acts as a call to the base URL `Route` for the application.
        '''
        return self.__route(*args, **kwargs)

    def add_credentials(self, username, password, path=None):
        if not self.__auth_manager:
            return

        path = path if str(path) else self.__url__
        self.__auth_manager.add_password(None, path, username, password)

    def __get_path__(self, attr):
        if not isstr(attr):
            return self._route(attr)

        path, query = URL.split(attr)

        # root path and base is not root, normalize path to subset of base
        if attr.startswith('/') and len(self.__url__.path):
            for element in self.__url__.path:
                if element != path[0]:
                    return attr
                del path[0]

        return self._route(self.__url__ + path, query)

    def __getattr__(self, attr):
        ''' __getattr__:
        Retrieves the existing method from the `Restler` object, if it does not
        exist, passes the attribute to the base route, returning any of it's
        existing methods or creates a child `Route` object for the new URL.

        Note: due to the existing method lookup, if your web API has a route
        for '[base URL]/base/', '[base URL]/base_class/', etc, they will not
        map properly as those are defined properties
        '''
        if attr in self.__dict__:
            return self.__dict__[attr]

        return self.__get_path__(attr)

    def __getitem__(self, attr):
        return self.__getattr__(attr)

    def __repr__(self):
        return 'Restler: ' + str(self.__url__)

    def __str__(self):
        return str(self.__url__)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __hash__(self):
        return reduce(lambda s, x: s ^ ord(x), str(self), 0)
