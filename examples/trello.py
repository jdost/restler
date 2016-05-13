from restler import Restler


def build(token, key):
    handler = Restler("https://api.trello.com/1/")
    handler._route._default_params["token"] = token
    handler._route._default_params["key"] = key
    handler._route.TRAILING_SLASH = False

    return handler
