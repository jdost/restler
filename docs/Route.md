# Routes

`Routes` are the individual objects that pertain to a specific path on the 
application.  They are in charge of issuing the requests and building a `Response`.
Each gets generated when chaining a path off of the base app (or when a URL is
returned in the response).

## Settings

Each `Route` needs a base `Restler` object and a path for construction.  You can
also include a default method (or "verb") to use when a request is made.  This
method would be something like "GET" or "POST" and be used if one isn't provided
when calling the object.

## Calling

When the object is "called" (i.e. it is executed like a function) it will attempt to
make an HTTP request to the associated URL (`Restler` base URL + associated path)
with the provided parameters.  The arguments that are keyed are going to be set to
parameters in the request except for the keys `method` and `headers`.  The method
of the request will be the default method of the object if it is not set in the
arguments (it can be changed at the `default_method` property of the object).

The `headers` argument will be merged with the class property of `__headers` (the
passed in argument overrides any set in the class property) and be used as the set
of headers for the request.  The other keyed arguments will be merged with the class
property of `__params` (the passed in arguments override any in the class property)
and be used as the data for the request body.  This data will be encoded as the 
common 'x-www-form-urlencoded' if no 'Content-Type' is set in the headers, otherwise
it will try to encode the data based on the 'Content-Type'.

NOTE: if no keyed params are set, but there is an unkeyed parameter and it is a 
string, it will be used as the request body (this is assuming that the encoding was
done by the user and the `Content-type` properly marked.

## Misc

The objects are comparable based on their full URL (so `app.foo != app.bar`).  They
also build child paths when requesting **any** property outside of the small set of
built in properties (`default_method`, `__path__`).

## Extending

If your application wants to extend the behavior of the route, there are a few 
places that are designed for easy extensibility.  The `__params` and `__headers`
properties of the class allow for setting default values for every request such as
auth tokens or 'Accepts' headers.  If you want to change the default method for a 
route, you can create your own `Route` object and override that in the constructor.
```python
class MyRoute(Route):
   def __init__(self, *args):
      Route.__init__(self, *args)
      self.default_method = "POST"
```
