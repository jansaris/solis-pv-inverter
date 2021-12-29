#!/usr/bin/env python3

import http.server as SimpleHTTPServer
import socketserver as SocketServer
import base64

PORT = 8000

class SimpleHTTPAuthHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    AUTH_HEADER = f'Basic {base64.b64encode("user:password".encode("ascii")).decode("ascii")}'

    def do_authhead(self, message):
        print(f'HTTP-401: {message}')
        self.send_error(401, message)
        self.send_header('WWW-Authenticate', 'Basic realm=\"Test\"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        print(self.headers)
        if self.headers['Authorization'] is None:
            self.do_authhead('Missing credentials')
        elif self.headers['Authorization'] == SimpleHTTPAuthHandler.AUTH_HEADER:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        else:
            print(f'Authorization mismatch. Actual ({self.headers["Authorization"]}) Expected({SimpleHTTPAuthHandler.AUTH_HEADER})')
            self.do_authhead('Wrong credentials')


Handler = SimpleHTTPAuthHandler
httpd = SocketServer.TCPServer(("", PORT), Handler)
print(f"Listen at {PORT}")
httpd.serve_forever()