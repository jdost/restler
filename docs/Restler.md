# Restler

Restler is the core handler for the library.  It is considered the base controller
of all subsequent routes created.  `Restler` is constructed with only one required
argument that specifies the base URL (ex. 'http://api.github.com/').

## Options

There is currently one optional argument of `cookies` that if `True` will add a
cookie tracking processor to all of the requests for the Restler instance.  Other
options can be added by extending the object (see below).

## Route Handling

By default the class for all routes is the `Route` class (this is controlled by the
`__route_class` property of the object).  Initially, a route is created for the
root of the web application and all calls and most attribute actions get delegated
to the base route.  If another class is desired, it can be done so via extending
the class (see below).

## URL Handlers

The HTTP requests are using a `urllib2.OpenerDirector` object that can have 
additional processors (see the `urllib2` documentation for more) like redirection
handling, proxying, or HTTP auth (to name a few).  The application opener is stored
in the `__opener__` property of the restler object.

## Extending

The `Restler` object can be extended to add whatever desired modifications you may
want to add.  If you want to use another custom `Route` class, just create your own
ancestor of `Restler` and override the value like:
```python
class MyRestler(restler.Restler):
   def __init__(self, *args, **kwargs):
      restler.Restler.__init__(self, *args, **kwargs)
      self.__route_class = MyRoute
      self.__route = self.__route_class('', self)
```
