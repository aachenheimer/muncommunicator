from socket import *

s = socket(AF_INET, SOCK_STREAM)

s.bind(('127.0.0.1', 7998))

s.listen(5)

while True:
    c = s.accept()
    
    msg = c[0].recv(1024)
    
    print("received msg %s" %msg.decode())
    
    c[0].close()