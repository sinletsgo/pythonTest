
import requests

url = "https://www.google.com"
r = requests.get(url)
cookies = r.cookies
print("-------------cookie----------------")
print(cookies)


header = r.headers
print("-------------header----------------")
print(header)

content = r.text
print("-------------body----------------")
print (cookies, content)


