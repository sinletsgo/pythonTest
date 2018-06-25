import requests
URL = 'http://192.168.110.116:8060/api/v1/addrecord'


# POST 방식 호출 (application/x-www-form-urlencoded)
data = {'name': ['shinsung', 'ssw'], 'city': 'seoul polytech'}
res = requests.post(URL, data=data)
print(res)





