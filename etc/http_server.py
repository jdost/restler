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
from multiprocessing import Process
from time import sleep

QUIET = False


def spawn(port):
    server = HTTPServer(("", port), TestHandler)
    server.serve_forever()


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

    def log_message(self, *args, **kwargs):
        if not QUIET:
            return BaseHTTPRequestHandler.log_message(self, *args, **kwargs)


class TestServer(object):
    def __init__(self, port=9000, threaded=False):
        self.port = port
        self.threaded = threaded
        if self.threaded:
            self.server = Process(target=spawn,
                                  args=(self.port,))
        else:
            self.server = HTTPServer(("", self.port), TestHandler)

    def start(self):
        if self.threaded:
            self.server.start()
            sleep(1)  # sleep 1 second to let socket get up and listening
        else:
            self.server.serve_forever()

    def stop(self):
        if self.threaded:
            self.server.terminate()
        else:
            self.server.server_close()

if __name__ == "__main__":
    import sys

    port = 9000
    quiet = False

    for arg in sys.argv:
        if arg in ['--quiet', '-q']:
            QUIET = True
        elif arg.isdigit():
            port = int(arg, 10)

    server = TestServer(port=port)
    server.start()
