from html.parser import HTMLParser
import requests

class myParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if (tag == "a"):
            for (attr, value) in attrs:
                #print("attr " + attr)
                #print("value " + value)
                if (attr == 'href' and value.startswith("http") == True) :
                    print(value)

url = "https://www.naver.com"

response = requests.get(url)

tempStr = response.text
print(tempStr)

parser = myParser()
parser.feed(tempStr)