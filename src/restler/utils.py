def isstr(s):
    try:
        return isinstance(s, str) or isinstance(s, unicode)
    except NameError:
        return isinstance(s, str)
