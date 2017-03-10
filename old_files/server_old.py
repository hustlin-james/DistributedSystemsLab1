import socket 
from threading import Thread 
from SocketServer import ThreadingMixIn 

import os
import json
 
# Multithreaded Python server : TCP Server Socket Thread Pool
class ClientThread(Thread): 
 
    def __init__(self,ip,port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
        self.username = ""
        print "[+] New server socket thread started for " + ip + ":" + str(port) 

    def send_msg(self,msg):
        conn.send(msg)
 
    def run(self): 
        while True:
            data = conn.recv(2048) 
            print "Server received data:", data
            #MESSAGE = raw_input("Multithreaded Python server : Enter Response from Server/Enter exit:")
            #if MESSAGE == 'exit':
            #   break
            req_data = json.loads(data)

            print("users")
            for t in threads:
                print(t.username)
                #print(dir(t))
                if t.username == "james2":
                    t.send_msg("TESSSST")

            if req_data['type'] == 'login':
                username = req_data['username']
                #Check the file database to see if the user exists

                #Login/Register new user
                if username in user_db and user_db[username] == 1:
                    print("user exists")
                else:
                    #We write to the file DB
                    user_db[username] = 1
                    user_db_str = json.dumps(user_db)
                    f = open("user_db","w")
                    f.write(user_db_str)
                    f.close()

                #Keeps track on the users that are logged on
                current_logged_in_users[username] = 1
                self.username = username
                conn.send("your logged in")

            if req_data['type'] == 'connect':
                username = req_data['username']

                if username in current_logged_in_users:
                    conn.send("you are connected")
                else:
                    conn.send("user is not logged on")
                
            conn.send(data)  # echo 
 
# Multithreaded Python server : TCP Server Socket Program Stub
#TCP_IP = '0.0.0.0' 
TCP_IP = '127.0.0.1'
TCP_PORT = 2005
BUFFER_SIZE = 20  # Usually 1024, but we need quick response 


current_logged_in_users = {}
user_db = {}
#Load the user database
if os.path.isfile("user_db"):
    f = open("user_db","r")
    user_db = json.loads(f.read())
 
tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
tcpServer.bind((TCP_IP, TCP_PORT)) 
threads = [] 
 
while True: 
    tcpServer.listen(4) 
    print "Multithreaded Python server : Waiting for connections from TCP clients..." 
    (conn, (ip,port)) = tcpServer.accept() 
    newthread = ClientThread(ip,port) 
    newthread.start() 
    threads.append(newthread) 
 
for t in threads: 
    t.join() 