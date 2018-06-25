#!/usr/bin/python
# from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import json
import re


PORT_NUMBER = 8090

# This class will handle any incoming request from
# a browser

class myHandler(BaseHTTPRequestHandler): # 이름그대로 BaseHTTPRequest를 Handler 하곘다! myHandler 상속
    # Handler for the GET requests

    # get, post 등으로 내가 처리하겠다.!
    def do_GET(self): #함수시작 = def,  def do_GET 자체가 약속된 것이고 self 즉 부모것 오버라이드 받은것.   내가 처리하겠다!

        # path 함수호출 주소(BaseHTTP.. class에 path가 있다. 가져다 쓰는것. 사용자가 request 날린 주소가 self.path로 들어간다.
        # 즉 /api/v1/getrecord/ 이 주소를 self.path에서 search 해서 맞으면 밑으로 내려가라. 아니면 else로 4o3 not found
        # re  -  레귤러익스프레션 정규표현식, * 모든것!
        # if None !=   not not 부정이니 맞다는 뜻. 프로그래머 관례라고 생각. 오히려 더 이렇게 사용하기도 한다고.
        if None != re.search('/api/v1/getrecord/*', self.path):
            recordID = (self.path.split('/')[-1]).split('?')[0]  #위에 /api/v1... 자르겠다! 다 자르면 4동강. -1 맨 뒤 * 걸 의미. 즉 * 가져와라. 그리고 ? 기준으로 자르라 1이면 밑으로
            print("recordID = ", recordID)

            # send_response, send_header,  wfile 등 전부 self 즉 부모 class에서 상속받은거다.
            if recordID == "1" :
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # Send the html message
                #  wfile 본문으로 응답 보내겠다!
                self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
                self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
                self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8")) # % url경로 까지 보냄.
                self.wfile.write(bytes("</body></html>", "utf-8"))
                #print(json.dumps(data, sort_keys=True, indent=4))
                #self.wfile.write(bytes(json.dumps(data, sort_keys=True, indent=4), "utf-8"))

            else: #1이 아니면 이곳와서 Bad
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
        # 아래 사이트에서 code 참고하셨다.
        # ref : https://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

try:
    # Create a web server and define the handler to manage the
    # incoming request

    # python 내장 class
    server = HTTPServer(('', PORT_NUMBER), myHandler) # myHandler 위에서 우리가 정의한 클래스, #  HTTPServer((''), '' 안에 공백 안넣으면 접속이 안된다.
    #server = ThreadedHTTPServer(('localhost', PORT_NUMBER), myHandler) #사용자들의 여러건 요청에 대한 응답을 처리 해야할경우 위  code 주석하고 ThreadedHTTPServer로 하는게 좋다
    print ('Started httpserver on port ' , PORT_NUMBER)

    # Wait forever for incoming http requests
    server.serve_forever() #계속 돌게 한다! (ctrl+c로 빠져나오지않는한)  , 여기서 서버 올라간다.

except KeyboardInterrupt: # KeyboardInterrupt 들어오면 close
    print ('^C received, shutting down the web server')
    server.socket.close()









