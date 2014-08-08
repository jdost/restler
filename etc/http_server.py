try:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from http.server import BaseHTTPRequestHandler, HTTPServer
try:
    from urlparse import parse_qs
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode, parse_qs
import json


class TestHandler(BaseHTTPRequestHandler):
    def handle_one_request(self):
        self.raw_requestline = self.rfile.readline(65537)
        self.parse_request()

        params = self.rfile.read(
            int(self.headers.get('Content-Length', '0')))
        params = parse_qs(params)

        data = {
            "path": self.path,
            "method": self.command,
            "params": params,
            "headers": dict(self.headers.items())
        }

        self.send_response(200)
        if self.headers.get('Accepts', 'application/json') == \
                'application/json':
            self.send_header('Content-type', 'application/json')
            data = json.dumps(data)
        elif self.headers.get('Accepts') == \
                'application/x-www-form-urlencoded':
            self.send_header('Content-type',
                             'application/x-www-form-urlencoded')
            data = urlencode(data)
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
