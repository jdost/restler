try:
    from urllib import urlencode
    from urllib2 import HTTPRedirectHandler
except ImportError:
    from urllib.parse import urlencode
    from urllib.request import HTTPRedirectHandler


def isstr(s):
    try:
        return isinstance(s, str) or isinstance(s, unicode)
    except NameError:
        return isinstance(s, str)


def to_urlstr(p):
    params = []
    if any([isinstance(v, list) for v in p.values()]):
        removals = []
        for k, v in p.items():
            if not isinstance(v, list):
                continue
            params += map(lambda v: (k, v), v)
            removals.append(k)
        for k in removals:
            del p[k]
    return urlencode(list(p.items()) + params)


class NoRedirectHandler(HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return HTTPRedirectHandler.http_error_302(self, req, fp, code,
                                                  msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302
