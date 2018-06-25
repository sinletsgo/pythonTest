#!/usr/bin/python
# from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import json
import re
from urllib.parse import parse_qs
from urllib.parse import urlparse
import cgi

PORT_NUMBER = 8060

# This class will handle any incoming request from
# a browser
class myHandler(BaseHTTPRequestHandler): # BaseHTTPRequestHandler 기본 라이브러리. myHandler가 상속받은것
# get 목록 조회, 콘텐츠 조회
# post 글 작성
    # Handler for the GET requests
    def do_GET(self):  # 오버라이드 받아서 호출된다. myHandler에서 자식으로 재정의. 클라이언트에서 겟방식 요청오면 do_GET이 처리

        print('Get request received')
        if None != re.search('/api/v1/getrecord/*', self.path): # url이 http://~/api/v1/getrecord/~ 형태인지 검사

            queryString = urlparse(self.path).query.split('=')[1]  # url이 /api/v1/getrecord?key=value 형태에서 value값을 찾는다.
                                                                    # query 하는 순간 ? 뒤에 것이 떨어짐. 거기서 split 하니 0,1 로 나눠지는것
            print("queryString = ", queryString)
            if None != queryString :
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                # Send the html message
                self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
                self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
                self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
                self.wfile.write(bytes("<p>Your query: %s</p>" % queryString, "utf-8"))
                self.wfile.write(bytes("</body></html>", "utf-8"))

            else:
                self.send_response(400, 'Bad Request: record does not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

    def do_POST(self):
        if None != re.search('/api/v1/addrecord/*', self.path):
            ctype, pdict = cgi.parse_header(self.headers['content-type']) # headers를 content-type로 하겠다. 이게 아니면 403으로 내려감!
            # cgi Common Gateway Interface
            print("ctype:", ctype)   # application/json
            print("pdict:", pdict)
            # {}  pdict: {'charset': 'UTF-8'}    사용자가 요청할때 UTF-8 같은걸 넣어서 보낼때 이곳에 들어간다.
            # 꼭 필요한건 아니지만, 혹시 server가 UTF-8 아니면 안받는 처리 하는 경우 대비해서 보내는것

             # Key - Value Pair의 컬렉션
            # 여기서부턴 고정
            if ctype == 'application/json': # josn 형식이면 밑으로
                content_length = int(self.headers['Content-Length']) # content_length 길이 변수에 대입
                # print("content_length:", content_length) # 47
                post_data = self.rfile.read(content_length)  # content_length 만큼 rfile 즉 read 읽고!
                print("post_data:", post_data) # b'{"this": ["is a test", "dd"], "received": "ok"}'  b는 byte 약자.
                receivedData = post_data.decode('utf-8') # 디코더 , 한글로 요청받았어도, 여기서 디코딩하니 ok
                print("receivedData:", receivedData) # {"this": ["is a test", "dd"], "received": "ok"}
                # 고정 끝

                # 여기서부터 바꿔야겠지. 주가정보를 가져와서 판단을 한다던가
                print(type(receivedData)) # <class 'str'>
                # Dict 형식으로 개발한다. 간단한 형식!
                tempDict = json.loads(receivedData) #  load your str into a dict 즉 STR -> DICT로 !
                tempDict['author'] = 'ssw' # tempDict 에 key : value 를  author:ssw 로 넣겠다!
                print(type(tempDict)) # <class 'dict'>
                print(tempDict)  # {'this': ['is a test', 'dd'], 'received': 'ok'}
                #

                self.send_response(200) # 200 response
                self.send_header('Content-type', 'application/json') # 요청온 사람에게 JOSN으로 주겠다!
                self.end_headers()
                self.wfile.write(bytes(json.dumps(tempDict), "utf-8")) # Dict형식을 JOSN형식 문자열로 덤프 하겠다!





            #url 인코딩 방식. 잘 안쓰지만 10%정도 사용.
            elif ctype == 'application/x-www-form-urlencoded':
                content_length = int(self.headers['content-length'])
                # trouble shooting, below code ref : https://github.com/aws/chalice/issues/355
                postvars = parse_qs((self.rfile.read(content_length)).decode('utf-8'),keep_blank_values=True)

                print(postvars)
                print(type(postvars))
                print(postvars.keys())

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes(json.dumps(postvars) ,"utf-8"))
            else:
                self.send_response(403)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        # ref : https://mafayyaz.wordpress.com/2013/02/08/writing-simple-http-server-in-python-with-rest-and-json/


        return


try:

    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print ('Started httpserver on port ' , PORT_NUMBER)

    # Wait forever for incoming http requests
    server.serve_forever()

except KeyboardInterrupt:
    print ('^C received, shutting down the web server')
    server.socket.close()
