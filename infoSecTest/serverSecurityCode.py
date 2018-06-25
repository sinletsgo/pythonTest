#!/usr/bin/python
# from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
import json
import re
import os


PORT_NUMBER = 8060
comments = []
# This class will handle any incoming request from
# a browser
class myHandler(BaseHTTPRequestHandler):

   def escape(self, s):
       s = s.replace("<", "&lt;")
       s = s.replace(">", "&gt;")
       s = s.replace("&", "&amp;")
       return s

    # Handler for the GET requests
   def do_GET(self):
        print('Get request received')
        if None != re.search('/api/v1/getrecord/*', self.path):

            queryString = urlparse(self.path).query.split('=')[1] # https://docs.python.org/3/library/urllib.parse.html
            
            queryString = self.escape(queryString)
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

        elif None != re.search('/favicon*', self.path):
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            print(os.getcwd())
            file = open(os.getcwd()+'/favicon.ico','rb') # 1.2KB = 1228 Bytes
            size = os.path.getsize(os.getcwd()+'/favicon.ico')
            print(size)
            s= file.read(size)
            self.wfile.write(s)
            file.close()
        else:
            self.send_response(400, 'Bad Request: record does not exist')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        # ref : https://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/


        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

try:

    # Create a web server and define the handler to manage the
    # incoming request
    #server = HTTPServer(('', PORT_NUMBER), myHandler)
    server = ThreadedHTTPServer(('', PORT_NUMBER), myHandler)
    print ('Started httpserver on port ' , PORT_NUMBER)

    # Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print ('^C received, shutting down the web server')
    server.socket.close()
