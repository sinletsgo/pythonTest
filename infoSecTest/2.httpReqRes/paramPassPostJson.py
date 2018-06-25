import requests, json

URL = 'http://192.168.110.116:8060/api/v1/addrecord'
data = {'outer key1': {'id': 'shin'},'outer key2': {'inner key': '0060'}, }
myHeader = {'Content-Type': 'application/json; charset=utf-8'}
# POST 방식 호출 (application/json)
res = requests.post(URL, headers=myHeader, data=json.dumps(data))
print(res)

