'''
Michael Pena
'''

import socket
import os
import threading
from server_functions import *

def web_server():
	HOST = '127.0.0.1'
	PORT = 1234

	# create socket, bind, and set the port to listen
	server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	server_socket.bind((HOST,PORT))
	server_socket.listen(5)

	print('Webserver running on port: ', PORT)

	while True:
		connection, address = server_socket.accept()

		#Create a thread for each connection coming from the browser
		request_handler = threading.Thread(target=connection_thread, args=(connection,))
		request_handler.start()

# run the webserver
if __name__ == '__main__':
	web_server()