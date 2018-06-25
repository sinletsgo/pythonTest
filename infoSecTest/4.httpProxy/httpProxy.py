import requests

http_proxy  = "http://153.149.168.44:3128" # https://free-proxy-list.net/
url = 'http://www.nate.com'
proxyDict = {"http"  : http_proxy }

r = requests.get(url, proxies=proxyDict)

print(r.text)

