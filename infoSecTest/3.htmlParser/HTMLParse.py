from html.parser import HTMLParser

import urllib.request

class myParser(HTMLParser): #HTMLParser상속 받은 myParser class
    def handle_starttag(self, tag, attrs): # starttag  ->   <
        if (tag == "a"): # a로 시작하는 tag 면 아래로
            for (attr, value) in attrs:
                print("attr " + attr)
                print("value " + value)
                if (attr == 'href' and value.startswith("http") == True) : #attr 속성값.
                    print(value)

url = "https://www.naver.com" #여기서 시작
request = urllib.request
response = request.urlopen(url)
tempStr = response.read().decode("utf-8")
print(tempStr)

parser = myParser() #  myParser 함수 parser 로 정의
# HTMLParser 안에 feed라는게 있다.
parser.feed(tempStr) # parser.feed 로 1번만 호출하면 myParser 함수가 계속 돌면서 tempStr에서 링크만 판별하지(내부에서 그렇게 정의해놈)
