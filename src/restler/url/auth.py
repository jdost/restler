try:
    import urllib2
except ImportError:
    import urllib.request as urllib2


class AuthManager(object):
    """ Simple wrapper around HTTP Auth registration and lookup.  Wraps the
    ``urllib2`` manager and provides a simple interface to add in new
    credentials.
    """
    def __init__(self, auths, url):
        self.url = url
        if isinstance(auths, urllib2.HTTPPasswordMgr):
            self._manager = auths
        else:
            self._manager = urllib2.HTTPPasswordMgrWithDefaultRealm()

        self + auths

    @property
    def handler(self):
        """ Valid ``urllib2`` request handler
        """
        return urllib2.HTTPBasicAuthHandler(self._manager)

    def __add__(self, auth):
        if isinstance(auth, tuple):
            self._manager.add_password(None, self.url, auth[0], auth[1])
        elif isinstance(auth, dict):
            self._manager.add_password(None, self.url, auth["username"],
                                       auth["password"])
        elif isinstance(auth, list):
            for a in auth:
                self + a
