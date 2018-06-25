import socket
import threading

class clientReq(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    #연결 test
    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = ("www.naver.com", 443)
        sock.connect(addr)
        print("Connected")


clients = []
for i in range(0,5): #5번 실행!
    s = clientReq()
    s.start()  #여기서 run 호출되서 돈다
    print("thread started ", i)
    clients.append(s)

for i in clients:
    i.join()


print(clients)
