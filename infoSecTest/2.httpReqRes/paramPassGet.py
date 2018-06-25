import requests
URL = 'http://192.168.110.116:8060/api/v1/getrecord'
#response = requests.get(URL)
#print(response.status_code)
#print(response.text)

# GET 방식 호출
params = {'key1': 'test', 'sin': '60'}
res = requests.get(URL, params=params)

