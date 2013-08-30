from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import urllib
import json


class TestHandler(BaseHTTPRequestHandler):
    def handle_one_request(self):
        self.raw_requestline = self.rfile.readline(65537)
        self.parse_request()

        params = self.rfile.read(
            int(self.headers.getheader('Content-Length', '0')))
        params = urlparse.parse_qs(params)

        data = {
            "path": self.path,
            "method": self.command,
            "params": params,
            "headers": self.headers.headers
        }

        self.send_response(200)
        if self.headers.getheader('Accepts', 'application/json') == \
                'application/json':
            self.send_header('Content-type', 'application/json')
            data = json.dumps(data)
        elif self.headers.getheader('Accepts') == \
                'application/x-www-form-urlencoded':
            self.send_header('Content-type', 'application/x-www-form-urlencoded')
            data = urllib.urlencode(data)
        self.end_headers()
        self.wfile.write(data)
        self.wfile.flush()
        return


class TestServer():
    def __init__(self, port=9000):
        self.port = port
        self.server = HTTPServer(("", self.port), TestHandler)

    def start(self):
        self.server.serve_forever()

    def stop(self):
        self.server.server_close()

if __name__ == "__main__":
    server = TestServer()
    server.start()
