from scapy.all import *
import sys

destIP="192.168.110.117"

def myPortScan(port):
    print("%d port scanning" % port)
    # sr1(IP(dst=destIP)/TCP(dport=port, flag="S"))

    # report_ports scapy에서 온것
    a=report_ports(destIP,port) #본인 ip때리면 결과안나오니까, destIP - 117로 때림
    print(a)
    print(type(a))
    if "open" in a: #open 문자열 있다면 ! 열린걸로 판단, 아래로 내려가서 write
        print("%d port is open." % port)
        file.write("%d port is open\n" % port)
        file.write("%s" % a)
        file.write("\n")


#report_ports("192.168.110.117",[22,25])
#sr1(IP(dst="192.168.110.117")/TCP(dport=(22,25), flags="S"))   
#sr1(IP(dst="192.168.110.117")/TCP(dport=[22,25], flags="S"))   

file = open("result.txt","w")   #
 
file.write("START PORT SCANNING") 
#myPortScan(22)  #22번 ssh
for i in range(1,66535):  # 1~ 66535 돌면서 myPortScan 호출!
    myPortScan(i)

