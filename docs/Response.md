# Response handling

When a response comes in, there is a default handler which tries to figure out as
much as it can about the response body.  This includes smart parsing and datatypes
for various formats, determining the MIME type of the response body and parsing
it accordingly, and adding additional methods based on contents of the headers.

## Datatypes

If the returned value (so no keys) matches either a relative URL (or an absolute URL 
that starts with the same base as the current response URL) a new `Request` object
will instead be returned (the `str` of the object will be the same).

If the returned value matches any of a set of patterns for dates/dates & times.  The
string will be parsed and returned as a `datetime` instance to be acted on.  This
structure will be extensible to have other formats come in (such as possible things
like timedeltas or other formats like inline markdown).  The `datetime` instance 
will be wrapped with an object that has a `str` of the original string.

## MIMEtypes

Starting off, the mimetype for JSON will be interpreted and handled.  Eventually, I 
would like to add XML (of some form), YML, and possibly others.  This is first 
determined by the MIMEtype of the response packet.  If there is not one set, it will
go through tests to see if any of these formats is used.

## Headers

Various headers can be used to determine more information on the response data.
Things such as the `Link` header will add methods for pagination of the response
type (calling the added methods will make the request to the targetted URL).  If
there are any cache setting headers, and a caching engine is in place, the response
will get registered in the cache holding and reused if subsequent request returns
with a no change.

## Response Codes

The response code will determine the various actions taken place.  If the response
is a 4xx or 5xx response code, a proper error type will be thrown (if error handling
is desired) or a full response object is returned with the status code set to the 
error and filled out accordingly.  

## Extending

The `Response` object can be extended a few ways.  Using the built in class methods
of `add_mimetype` and `add_datatype` to add handlers for data transforms or response
mimetype conversion.  Both take two arguments, for `add_mimetype` the first argument
is a string of the mimetype the handler is for, for `add_datatype` is a function 
that outputs a boolean on whether the value matchs the criteria for the datatype
conversion.  This function takes two arguments, the first is the `Response` object
itself and the second is the value.  If either of these tests pass (the mimetype is
the same as the response or the detection function succeeds) the second argument is
used, it is a handler function that takes care of transforming the string provided
into a rich(er) data structure such as a `dict` or `datetime`.  A simple example
for mimetypes would be:
```python
Response.add_mimetype("application/json": lambda d: json.loads(d))
```

NOTE: the URL and datetime datatype conversion use this interface to be set up, see
the source to see how these are done, same for the json and urlencoded mimetypes.
