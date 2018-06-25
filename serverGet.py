#!/usr/bin/python
# from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
import json
import re


PORT_NUMBER = 8060
comments = []
# This class will handle any incoming request from
# a browser
class myHandler(BaseHTTPRequestHandler):


    # Handler for the GET requests
    def do_GET(self):
        print('Get request received')
        if None != re.search('/api/v1/getrecord/*', self.path):

            # = 으로 할경우에만 오류안난다. 다르게 요청할경우에 오류안나려면 예외 처리를 해줘야 함.
            queryString = urlparse(self.path).query.split('=')[1] # https://docs.python.org/3/library/urllib.parse.html

            print("queryString = ", queryString)

            if None != queryString :
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                query = queryString

                tmpStr = "%s 님이 요청한 검색어 : %s "%( str(self.client_address), query)
                comments.append(tmpStr)

                self.wfile.write(bytes("<html><head><title>Search Results</title></head>", "utf-8"))
                self.wfile.write(bytes("<body>", "utf-8"))
                self.wfile.write(bytes("<P><font size='20'><B>댓글놀이</B></font></P>", "utf-8"))
                self.wfile.write(bytes("---------------------------------------------------------", "utf-8"))
                for comment in comments:
                    self.wfile.write(bytes("<P>%s</P>" %comment,"utf-8"))

                self.wfile.write(bytes("</body></html>", "utf-8"))

            else:
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        # ref : https://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/


        return

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
