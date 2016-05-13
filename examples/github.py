from restler import Restler


def build(token, url="https://api.github.com/"):
    handler = Restler(url)
    handler._route._default_headers.append(("Authorization",
                                            "token " + token))
    handler._route.TRAILING_SLASH = False

    return handler
