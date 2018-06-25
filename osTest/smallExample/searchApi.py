import os
import sys
import urllib.request
import json

client_id = "NtF6I1bYeQpw1Z_V_gH0"
client_secret = "o_tA7AtX2a"
encText = urllib.parse.quote("한국폴리텍대학")
url = "https://openapi.naver.com/v1/search/blog?query=" + encText  
# url = "https://openapi.naver.com/v1/search/blog.xml?query=" + encText 
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request)
rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
    print(response_body.decode('utf-8'))
    #jsonString = json.dumps(response_body.decode('utf-8'),indent=4)
    #print(jsonString)
    dict = json.loads(response_body.decode('utf-8'))
    print(dict['items'])
    for a in dict['items']:
        print("\n")
        print("title :" + a['title'])
        print("\n")
        print("bloggername :"+ a['bloggername'])
        print("\n")
        print("link : " + a['bloggerlink'])
        print("\n")
else:
    print("Error Code:" + rescode)



