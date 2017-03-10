# chat_client.py

import sys
import socket
import select
import random
 
BUFFER_SIZE = 4096
def gen_fake_ip_id():
    my_str = '127.'
    my_str = my_str + str(random.randint(0,9)) + '.'
    my_str = my_str + str(random.randint(0,9)) + '.'
    my_str = my_str + str(random.randint(0,9))

    return my_str

def chat_client():

    print 'Usage : python chat_client.py hostname port'
    host = '127.0.0.1'
    port = 8018
    fake_ip_id = gen_fake_ip_id()

    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])

    if len(sys.argv) == 2:
        fake_ip_id = sys.argv[1]
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()
     

    print 'Connected to remote host.'
    print 'unique ip: %s'%(fake_ip_id)

    s.send(fake_ip_id)
     
    while 1:

        try:

            socket_list = [sys.stdin, s]
            # Get the list sockets which are readable
            ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
            
            for sock in ready_to_read:             
                if sock == s:
                    # incoming message from remote server, s
                    data = sock.recv(BUFFER_SIZE)
                    if not data :
                        print '\nDisconnected from chat server'
                        sys.exit()
                    else :
                        #print data
                        sys.stdout.write(data)
                        sys.stdout.write('[Me] '); 
                        sys.stdout.flush()     
                
                else :
                    # user entered a message
                    msg = sys.stdin.readline()
                    s.send(msg)
                    sys.stdout.write('[Me] '); sys.stdout.flush() 
        except:
            sys.exit(0)


if __name__ == "__main__":

    sys.exit(chat_client())