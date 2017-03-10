#! /usr/bin/env python
# coding: utf-8
#
# WhatsUp Client
# Yet another simple socket multi-user chating program
#
#
# @author: Xin Wang <sutarshow#gmail.com>
# @date: 18-09-2013
#

import socket
import time
import logging
import sys
import random

HOST = '127.0.0.1'
PORT = 8018
TIMEOUT = 5
BUF_SIZE = 1024

class ChatClient():
    def __init__(self, host=HOST, port=PORT,fake_ip_id=''):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        logging.info('Connecting to %s:%s' % (host, port))

        self.sock.send(fake_ip_id)

        while 1:
            try:
                buf = self.sock.recv(BUF_SIZE)
                sys.stdout.write(buf)
                cmd = raw_input()
                if cmd.strip() == '!q':
                    sys.exit(1)
                self.sock.send(cmd)
            except:
                self.sock.close()

def gen_fake_ip_id():
    my_str = '127.'
    my_str = my_str + str(random.randint(0,9)) + '.'
    my_str = my_str + str(random.randint(0,9)) + '.'
    my_str = my_str + str(random.randint(0,9))

    return my_str

def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s: %(message)s',
                        datefmt='%d/%m/%Y %I:%M:%S %p')    

    fake_ip_id =gen_fake_ip_id()
    
    if len(sys.argv) > 1:
        fake_ip_id = sys.argv[1]

    chat_client = ChatClient(fake_ip_id=fake_ip_id)

if __name__ == '__main__':
    main()