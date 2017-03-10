#! /usr/bin/env python
import socket
import threading
import time
import logging
import sys

HOST = ''
PORT = 8018
TIMEOUT = 5
BUF_SIZE = 16384

#Input: None
#Output: None
#Summary:
#Represents a client object to be used for functions
class Client():
    def __init__(self,conn,addr,fake_ip,username,password,is_online,last_login):
        self.conn = conn
        self.addr = addr
        self.fake_ip = fake_ip
        self.username = username
        self.password = password
        self.is_online = is_online
        self.last_login = last_login
        self.connected_client = None
        self.alert_users = []

#Input: None
#Output: None
#Summary:
#This is the ChatServer Thread Object that is created when ever a new connection is detected.
#It contains functions and properties to communication with the client that it represents.
class ChatServer(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.ip = self.addr[0]
        self.username = ''

    #Input: self object, string
    #Output: None
    #Summary:
    #Helper method for sending out messages to the client
    def print_indicator(self, prompt):
        self.conn.send('%s\n>> ' % (prompt,))

    #Input: self object, string
    #Output: None
    #Summary:
    #This is to check for special commands that the user can send to the server such as logging and connecting/disconnecting to
    #a user.  If it finds one of those commands it will run a function to process or it just finishes and the server goes
    #back to the run loop
    def check_keyword(self, buf):
        if buf.find('!q') == 0:
            self.logoff()

        if buf.find('!alert') == 0:
            tokens = buf.split()
            if tokens > 1:
                client = get_user_by_addr(self.addr)
                alert_username = tokens[1]
                alert_user = get_user_by_username(alert_username)

                #Check if the alert user is already there
                alert_exists = False
                for a in client.alert_users:
                    if a.username == alert_username:
                        alert_exists = True
                        break
                
                if alert_user != None and alert_username != client.username and alert_exists == False:
                    client.alert_users.append(alert_user)
                    self.conn.send('## You added %s to alert when you sign on. \n'%alert_username)
                else:
                    self.conn.send('## cant find user.\n>>')

        if buf.find('!disconnect') == 0:
            logging.info('Disconnect Requested')
            client = get_user_by_addr(self.addr)
            if client.connected_client != None: 
                connected_username = client.connected_client.username
                client.connected_client.conn.send("*private* %s has disconnected from you. \n>>"%self.username)
                client.connected_client = None
                self.conn.send('## You have been disconnected from %s \n>>'%connected_username)
        
        if buf.find('!connect') == 0:
            logging.info('Connect Requested')
            client = get_user_by_addr(self.addr)
            #Split the msg to get the second part which contains the username
            tokens = buf.split()
            if tokens > 1:
                if client.connected_client == None:
                    connect_username = tokens[1]
                    connected_client = get_user_by_username(connect_username)
                    if connected_client != None and connected_client.is_online == True and connected_client.username != self.username:
                        client.connected_client = connected_client
                        self.conn.send('## You have been connected to %s \n'%connect_username)
                    else:
                        self.conn.send('## cant find user.\n>>')
                else:
                    self.conn.send('## you are already connected to a client.\n>>')
            else:
                self.conn.send('## cant find user.\n>>')

    #Input: Self Object
    #Output: None
    #Summary:
    #This function will log the user out by setting the is_online to false.  Thus it never deletes the client 
    #so that the next time the client will log in the server will remember them.  It then closes the connection.
    def logoff(self):
        client = get_user_by_addr(self.addr)
        client.is_online = False

        if client.connected_client != None:
            client.connected_client.conn.send("*private* %s has disconnected from you. \n>>"%self.username)
            client.connected_client = None
        
        logging.info('Loggin Off %s:%s,username: %s' %(self.addr[0], self.addr[1],self.username))
        self.conn.send('## Bye!\n')
        self.conn.close()
        exit()

    #Input: Self Object
    #Output: None
    #Summary:
    #This function handles the beginning when the client has connected to the server.  
    #The fake ip that was passed in is so the server can check for persistent sessions. I use the
    #fake ip as an unique identifier right when they log in so that I can check if they have an account already.
    #I can't use the IP and Port because I run this on localhost so all client will have the same IP and the Port changes.
    #If the server detects that this user hasnt registered then it prompts them for a username and password otherwise
    #it will just prompt them for a password.  If the user was new it create a client and adds it to the clients global object.
    #Otherwise it will just find the client in the clients global and set is_online to true.
    def login(self):
        global clients

        #Using fake ip to simulate logging in from different IP's
        header_info = get_http_header_info(self.conn.recv(BUF_SIZE).strip())
        fake_ip = header_info['msg']
        
        logging.info('Connected from: %s:%s,fake_ip:%s' %(self.addr[0], self.addr[1],fake_ip))
        logging.info('%s %s %s'%(header_info['request_type'], header_info['date'],header_info['length']))

        msg = '\n## Welcome to Chat\n## Enter `!q` to loggoff. Enter `!connect [username]` to talk to another client and !disconnect to leave. \n'

        #Check to see if the user is already signed up
        client = None
        for c in clients:
            if c.fake_ip == fake_ip:
                client = c
        
        #If client is None then he is not in the list of users and we have to register him
        if client is None:
            msg += '## Please enter your username:'
            self.print_indicator(msg)

            username = ''
            while 1:
                header_info =  get_http_header_info(self.conn.recv(BUF_SIZE).strip())
                username = header_info['msg']
                logging.info('%s %s %s'%(header_info['request_type'], header_info['date'],header_info['length']))

                if is_username_taken(username) == True:
                    self.print_indicator(
                        '## This username already exists, please try another')
                else:
                    break
            
            self.print_indicator('## Hello %s, please set your password:' % (username,))
            header_info = get_http_header_info(self.conn.recv(BUF_SIZE).strip())
            password = header_info['msg']
            logging.info('%s %s %s'%(header_info['request_type'], header_info['date'],header_info['length']))

            self.print_indicator('## Welcome, enjoy your chat')

            logging.info('%s:%s,fake_ip:%s,logged as %s' % (self.addr[0],self.addr[1],fake_ip,username))

            c = Client(self.conn,self.addr,fake_ip,username,password,True,time.ctime())
            clients.append(c)
            self.username = username

        else:
            #Check if the user is already online
            c = get_user_fake_ip(fake_ip)
            self.username = c.username

            if is_user_online(c.username) == True:
                self.conn.send('## You are already online!\n')
                self.conn.close()
                exit()
            else:
                 msg += '## Hello %s, please enter your password:' % (c.username,)
                 self.print_indicator(msg)
                 
                 while 1:
                    header_info = get_http_header_info(self.conn.recv(BUF_SIZE).strip())
                    password = header_info['msg']
                    logging.info('%s %s %s'%(header_info['request_type'], header_info['date'],header_info['length']))

                    c = is_password_correct(c.username,password)
                    if c == None:
                        self.print_indicator(
                            '## Incorrect password, please enter again')
                    else:
                        self.print_indicator(
                            '## Welcome back, last login: %s' % c.last_login)
                        c.last_login = time.ctime()
                        c.is_online = True
                        c.conn = self.conn
                        c.addr = self.addr
                        c.connected_client = None
                        
                        #Alert users
                        if len(c.alert_users) > 0:
                            alert_msg = 'These users are online: '
                            for a in c.alert_users:
                                if a.is_online == True:
                                    alert_msg =  alert_msg + a.username+ '; '
                            self.print_indicator(alert_msg)

                        break
    #Input: Self Object, message to send to client
    #Output: None
    #Summary: 
    #This is just a helper method to do logic on which clients I should send the message.  Whether to send the message
    #to a private client session or just send it globally.
    def broadcast(self, msg):

        client = get_user_by_username(self.username)

        #This user has a private message session with another user
        #else the user has no private session so output globally
        if client.connected_client != None:
            client.connected_client.conn.send('*private* %s \n>>'%(msg))
            self.conn.send('>>')
        else:
            for c in clients:
                c.conn.send(msg + '\n>>')
    #Input: self object
    #Output: None
    #Summary:
    #This run function gets called whenever a new thread is created.  It will then attempt to using the connection
    #information to login/register the user and afterwards it will constantly listen to the client socket for messages.
    def run(self):
        global clients

        self.login()

        print("login done")

        while 1:
            try:
                self.conn.settimeout(TIMEOUT)
                header_info = get_http_header_info(self.conn.recv(BUF_SIZE).strip())
                buf = header_info['msg']

                logging.info('%s %s %s'%(header_info['request_type'], header_info['date'],header_info['length']))
                logging.info('%s:%s, msg: %s' % (self.addr[0],self.addr[1], buf))
                # check features
                if not self.check_keyword(buf):
                    # client broadcasts message to all
                    self.broadcast('%s: %s' % (self.username, buf))
            except Exception, e:
                # Connection Timed out
                pass

#Input: header string
#Output: header string info as a dictionary
#Summary: 
#Extracts the header info into a dictionary
def get_http_header_info(header_str):
    tokens = header_str.split("\n")

    if len(tokens) > 6:
        msg = tokens[len(tokens)-1]
        return {'msg':msg, 'request_type':tokens[0],'date':tokens[5],'length':tokens[6]}
    else:
        return  {'msg':'', 'request_type':'','date':'','length':''}

#The following functions are helpers to find the various clients thats kept track by the server.
def get_user_by_username(username):
    my_client = None
    for c in clients:
        if c.username == username:
            my_client = c
            break
    return my_client

def get_user_by_addr(addr):
    my_client = None
    for c in clients:
        if c.addr[0] == addr[0] and c.addr[1] == addr[1]:
            my_client = c
            break
    return my_client

def get_user_fake_ip(fake_ip):
    my_client = None
    for c in clients:
        if c.fake_ip == fake_ip:
            my_client = c
            break
    return my_client

def is_password_correct(username,password):
    my_client = None
    for c in clients:
        if c.username == username and c.password == password:
            my_client = c
            break
    return my_client

def is_user_online(username):
    is_online = False
    for c in clients:
        if c.username == username and c.is_online == True:
            is_online = True
            break
    return is_online

def is_username_taken(username):
    is_taken = False
    for c in clients:
        if c.username == username:
            is_taken = True
            break
    return is_taken

#Input: None
#Output: None
#Summary:
#Sets up the host and port the server will listen to and constantly listens for connections.
def main():
    global clients
    clients = []

    # logging setup
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')
    # set up socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print '-= Chat Server Started =-'
    print '>> Listening on:', PORT
    
    while 1:
        try:
            conn, addr = sock.accept()
            server = ChatServer(conn, addr)
            server.start()
        except Exception, e:
            print e      

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print 'Exiting Server Program'
        for c in clients:
            c.conn.close()
        sys.exit()