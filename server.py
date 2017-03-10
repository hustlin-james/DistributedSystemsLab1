#! /usr/bin/env python

import socket
import threading
import time
import logging

HOST = ''
PORT = 8018
TIMEOUT = 5
BUF_SIZE = 1024

class Client():
    def __init__(self,conn,addr,fake_ip,username,password,is_online,last_login):
        self.conn = conn
        self.addr = addr
        self.fake_ip = fake_ip
        self.username = username
        self.password = password
        self.is_online = is_online
        self.last_login = last_login

class ChatServer(threading.Thread):
    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.ip = self.addr[0]

    def print_indicator(self, prompt):
        self.conn.send('%s\n>> ' % (prompt,))

    def check_keyword(self, buf):
        if buf.find('!q') == 0:
            self.logoff()

    def logoff(self):
        global clients

        for c in clients:
            if c.addr[0] == self.addr[0] and c.addr[1] == self.addr[1]:
                c.is_online = False
                break

        self.conn.send('## Bye!\n')
        self.conn.close()
        exit()

    def login(self):
        global clients

        #Using fake ip to simulate logging in from different IP's
        fake_ip = self.conn.recv(BUF_SIZE).strip()
        logging.info('Connected from: %s:%s,fake_ip:%s' %(self.addr[0], self.addr[1],fake_ip))

        msg = '\n## Welcome to Chat\n## Enter `!q` to loggoff\n'

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
                username = self.conn.recv(BUF_SIZE).strip()
                if is_username_taken(username):
                    self.print_indicator(
                        '## This username already exists, please try another')
                else:
                    break
            
            self.print_indicator('## Hello %s, please set your password:' % (username,))
            password = self.conn.recv(BUF_SIZE)
            self.print_indicator('## Welcome, enjoy your chat')

            logging.info('%s:%s,fake_ip:%s,logged as %s' % (self.addr[0],self.addr[1],fake_ip,username))

            c = Client(self.conn,self.addr,fake_ip,username,password,True,time.ctime())
            clients.append(c)
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
                 # print accounts
                 self.print_indicator(msg)
                 
                 while 1:
                    password = self.conn.recv(BUF_SIZE).strip()
                    c = is_password_correct(c.username,c.password)
                    if c == None:
                        self.print_indicator(
                            '## Incorrect password, please enter again')
                    else:
                        self.print_indicator(
                            '## Welcome back, last login: %s' % c.last_login)
                        c.last_login = time.ctime()
                        c.is_online = True
                        break

    def run(self):
        global clients
        
        self.login()
        while 1:
            try:
                self.conn.settimeout(TIMEOUT)
                buf = self.conn.recv(BUF_SIZE).strip()
                logging.info('%s:%s, msg: %s' % (self.name, self.addr[0],self.addr[1], buf))
                # check features
                if not self.check_keyword(buf):
                    # client broadcasts message to all
                    self.broadcast('%s: %s' % (self.name, buf), clients)
            except Exception, e:
                # Connection Timed out
                pass

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