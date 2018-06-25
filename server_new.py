#!/usr/bin/python
# from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import json
import re



PORT_NUMBER = 8060

# This class will handle any incoming request from
# a browser

class myHandler(BaseHTTPRequestHandler):
    # Handler for the GET requests

    def do_GET(self):
        if None != re.search('/api/v1/getrecord/*', self.path):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers() n

            # Send the html message
            self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><p> test</p>", "utf-8"))
            self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))

        return
                #print(json.dumps(data, sort_keys=True, indent=4))
                #self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
try:

    # Create a web server and define the handler to manage the
    # incoming request

    server = HTTPServer(('', PORT_NUMBER), myHandler)
    #server = ThreadedHTTPServer(('localhost', PORT_NUMBER), myHandler)
    print ('Started httpserver on port ' , PORT_NUMBER)

    # Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print ('^C received, shutting down the web server')
    server.socket.close()
