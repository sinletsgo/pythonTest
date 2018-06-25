import socket
import threading

class clientReq(threading.Thread):

    def __init__(self, number):
        threading.Thread.__init__(self)
        self.number = number

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = ("www.naver.com", 443)
        sock.connect(addr)
        print("Connected " +str(self.number))


clients = []
for i in range(0,5):
    s = clientReq(i)
    s.start()
    print("thread started ", i)
    clients.append(s)

for i in clients:
    i.join()

