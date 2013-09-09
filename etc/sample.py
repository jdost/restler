import sys
try:
    import urllib2
except ImportError:
    import urllib.request as urllib2
from restler import Restler

JSON_TYPE = {"Content-Type": "application.json"}
FORM_ACCEPTS = {"Accepts": "application/x-www-form-urlencoded"}

app = Restler("http://127.0.0.1:9000")
# Basic call
try:
    response = app()
except urllib2.URLError as err:
    print(err)
    print("Make sure you have the `etc/http_server.py` script running")
    sys.exit(1)
print(response.data)
# Call with URL parameters
response = app.test(foo="bar")
print(response.data)
# POST with parameters
response = app.test("POST", foo="bar")
print(response.data)
# Set HTTP Headers
response = app.test(headers=JSON_TYPE, foo="bar")
print(response.data)
# Set the response mimetype in header
response = app.test(headers=FORM_ACCEPTS, foo="bar")
print(response.data)
# Convert response value to datetime
response = app.test(date="10/12/12")
print(response.data)
print(response.data['params']["date"])
# Convert response value to Restler Route
response = app.test(url="/test2")
print(response.data['params']['url'])
