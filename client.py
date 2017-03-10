#! /usr/bin/env python
import sys
import socket
import select
import random
import time
 
#Input: None
#Output: string representing a fake ip
#Summary:
#This just generates a fake ip using random numbers, although identifier would suffice.
def gen_fake_ip_id():
    my_str = '127.'
    my_str = my_str + str(random.randint(0,9)) + '.'
    my_str = my_str + str(random.randint(0,9)) + '.'
    my_str = my_str + str(random.randint(0,9))

    return my_str

#Input: None
#Output: None
#Summary:
#This is the main function of the chat client.  It first connects to the server and sends its fake ip identifier
#which will allow the server to prompt what the client should do next.  Afterwards the client will constantly 
#listen for input either from the server or the keyboard.  If it is from the server it outputs to the terminal
#while if it is from the keyboard it will send to the server.  This part contains select which only runs on Linux based systems.
def chat_client():

    global BUFFER_SIZE
    global HOST 
    global PORT

    BUFFER_SIZE = 16384
    HOST = '127.0.0.1'
    PORT = 8018

    print 'Usage : python chat_client.py hostname port'
    fake_ip_id = gen_fake_ip_id()

    if len(sys.argv) == 3:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])

    if len(sys.argv) == 2:
        fake_ip_id = sys.argv[1]
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((HOST, PORT))
    except :
        print 'Unable to connect'
        sys.exit()

    print 'Connected to remote host.'
    print 'unique ip: %s'%(fake_ip_id)

    s.send(create_http_request(fake_ip_id))
     
    while 1:

        try:
            socket_list = [sys.stdin, s]
            # Get the list sockets which are readable
            ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
            
            for sock in ready_to_read:             
                if sock == s:
                    # incoming message from remote server
                    data = sock.recv(BUFFER_SIZE)
                    if not data :
                        print '\nDisconnected from chat server'
                        sys.exit()
                    else :
                        sys.stdout.write(data)
                        sys.stdout.flush()     
                else :
                    # user entered a message
                    msg = sys.stdin.readline()
                    s.send(create_http_request(msg))
        except:
            s.send(create_http_request('!q'))
            data = s.recv(BUFFER_SIZE)
            if data != '':
                print("server: %s"%data)
            print("Interrupted.  Exiting....")
            sys.exit()

#Input: None
#Output: Http Request string
#Summary:
#This creates the HTTP Request Information to send to the server.  All Requests are using POST.
def create_http_request(msg):
    req = "POST / HTTP/1.1\n"
    req = req+"Host: "+HOST+":"+str(PORT)+"\n"
    req = req+"Accept: text/plain"+"\n"
    req = req+"Content-Type: text/plain"+"\n"
    req = req+"Connection: keep-alive"+"\n"
    req = req+"Date: "+time.ctime()+"\n"
    req = req+"Content-Length: "+ str(utf8len(msg))+"\n\n"
    req = req+msg
    return req
#Input: string
#Output: number of bytes
#Summary:
#This computes the size of the messages that is being sending.
def utf8len(s):
    return len(s.encode('utf-8'))
    
if __name__ == "__main__":
    chat_client()