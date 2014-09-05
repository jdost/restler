# RESTler

Status: ![Travis Status](https://travis-ci.org/jdost/restler.svg?branch=master)

RESTler is a python library I dreamed up that maps Object+method calls to RESTful
URL requests.  The idea is that you create a base RESTler object for the root of the
RESTful web application and then use method calls to get sub URLs and then use some
keyword attributes to make various requests to the created route, with built in
response handling.  This should make it easy to wrap a nice RESTful API into a 
simple python library.

## Example

``` python
>> flickr = Restler('http://flickr.com/api')
>> photos = flickr.photos
>> photos.__url__
'http://flickr.com/api/photos/'
```

## Getting Started

If you have a RESTful API you want to wrap, just use the `Restler` constructor to
create the base entry point of the application.  Then use the resulting object to
access the sub-routes of the application.  Every attribute maps to a level of the
URL, so `application.users.asdf` would request from `(application base)/users/asdf/`

## Route Object

The `Route` object returned from each attribute of the route has a series of
methods to help in accessing the current route or child routes.  The object itself
is calleable which maps to a `GET` request on the object.  Any other attributes will 
map to sub URLs of the current URL the `Route` maps to.

## Response Object

Any request made via a `Route` will return a `Response` object.  This object will
encapsulate the basic request with some helpers built in.  The main helper is that
the object's representation will map to the clearest form of the response data.  If
this is a JSON string, it will be parsed, if it is an XML document, it will be a
pointer to the XML document, if it is a plaintext string, it will just be a plain
string.  The headers for the response will be accessible as well via a reserved
property of the response.

### Example

``` python
workhammer = Restler('http://workhammer.herokuapp.com')
login = workhammer.login("post", username='admin', password='password')
if login.code > 300:
   throw "Login failed"

players = workhammer.player()
player = workhammer.player[players[0].id]()
```
