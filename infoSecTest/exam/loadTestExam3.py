import socket
import threading
import requests

resultList = [];

class clientReq(threading.Thread):
    def __init__(self, number):
        threading.Thread.__init__(self)
        self.number = number
    def run(self):
        URL = 'http://192.168.110.116:8060/block/getBlockData'
        response = requests.get(URL)
        # print(response.status_code)
        # print(response.text)
        resultList.append(response.text)

        # GET 방식 호출
        params = {'key1': 'test', 'sin': '60'}
        res = requests.get(URL, params=params)
        print(res)
        print("Connected " +str(self.number))

clients = []
for i in range(0,5):
    s = clientReq(i)
    s.start()
    print("thread started ", i)
    clients.append(s)

for i in clients:
    i.join()
print("response 결과: ", resultList[0]);
