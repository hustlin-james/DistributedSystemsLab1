# DistributedSystemsLab1
Chat Program

This program only works on a Linux based environment, mainly because I am using the python 'select' module which
allows the program to wait to get messages from the server.  For this to work on windows I would need to
use the Modify to use the WinSock library.

To start server:

python server.py

To start a client:

python client.py

options for client:
you can pass in the hostname and port directly in the command line but these must match the server options.
you can pass in a fake ip which the server will use as a identifier to check for persistent sessions.
If no options are passed the program will set defaults.

python chat_client.py [hostname] [port]
python client.py [fake_ip_id] 


References:
https://gist.github.com/owainlewis/3217710
http://www.bogotobogo.com/python/python_network_programming_tcp_server_client_chat_server_chat_client_select.php
http://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only