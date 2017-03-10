# Python TCP Client A
import socket 
import json
import sys
import select

host = '127.0.0.1'
port = 2005
BUFFER_SIZE = 2000 



username = raw_input('login/register as: ')
choice = 0

tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpClient.connect((host, port))

req = {'type':'login', 'username':username}
tcpClient.send(json.dumps(req))
res = tcpClient.recv(BUFFER_SIZE)

while choice != 1 and choice != 2:
    print "Please Choose: "
    print "1. Connect to user"
    print "2. Logout"
    choice = raw_input("choice: ")
    choice = int(choice)


if choice == 1:
    #Send to the server and register to the server if the user is not there
    req = {'type':'connect','username':'test'}
    reqStr = json.dumps(req)
    tcpClient.send(reqStr)
    data = tcpClient.recv(BUFFER_SIZE)
    print(data)
    print("choice 1")


#MESSAGE = raw_input("tcpClientA: Enter message/ Enter exit:") 

#while MESSAGE != 'exit':
#while True:
    #tcpClient.send(MESSAGE)     
    #data = tcpClient.recv(BUFFER_SIZE)
    #print " Client2 received data:", data
    #MESSAGE = raw_input("tcpClientA: Enter message to continue/ Enter exit:")

while 1:
    socket_list = [sys.stdin,tcpClient]
    ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
    
    for sock in ready_to_read:             
                if sock == tcpClient:
                    # incoming message from remote server, s
                    data = sock.recv(4096)
                    if not data :
                        pass
                        #print '\nDisconnected from chat server'
                        #sys.exit()
                    else :
                        #print data
                        sys.stdout.write(data)
                        sys.stdout.write('[Me]: '); sys.stdout.flush()     
                
                else :
                    # user entered a message
                    msg = sys.stdin.readline()
                    tcpClient.send(msg)
                    sys.stdout.write('[Me]: '); sys.stdout.flush() 

#tcpClient.close()
 


#while MESSAGE != 'exit':
#    tcpClientA.send(MESSAGE)     
#    data = tcpClientA.recv(BUFFER_SIZE)
#    print " Client2 received data:", data
#    MESSAGE = raw_input("tcpClientA: Enter message to continue/ Enter exit:")
 
#tcpClientA.close() 