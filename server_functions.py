'''
Michael Pena
'''
import os
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime


# this gets the current time for the date field in the response header. Returns data to add_header_data
def get_time():
	now = datetime.now()
	stamp = mktime(now.timetuple())
	return format_date_time(stamp)


# this gets the time for last modified field in the response header. Returns data to add_header_data
def get_last_modified(filename):
	modified_time = os.stat(filename).st_mtime
	return format_date_time(modified_time)


# this adds the header data to the response. Returns data to connection_thread
def add_header_data(header, filename, body):
	header += "Date: " + get_time() + "\n"
	header += "Server: Michaels-Python-Server (custom)\n"
	header += "Connection: Closed\n"
	header += "Content-Length: " + str(len(body)) + "\n"
	# if its a 404 error this field is not added since the file does not exist
	if os.path.exists(filename):
		header += "Last-Modified: " + get_last_modified(filename) + "\n"
	return header


# this function sends the response with the body and header
def send_response(connection, header, body):
	response = header.encode('utf-8')
	response += body

	# print("***Response sent***\n", response, '\n***End Response***\n') # debugging purposes

	connection.sendall(response)
	connection.close()

# this parses the http request, generates the status code, and composes the response message
def connection_thread(connection):
	request = connection.recv(1024).decode('utf-8')  # recieve and decode the string into a readable format
	print(request)

	# split the response by spaces and place into the list
	response_list = request.split(' ')

	# this gets the file name from the request
	if response_list != '':
		file_requested =  response_list[1]

	# this removes the '/' character in the file name if it exists
	if '/' in file_requested:
		file_requested = file_requested.replace( '/', '')

	fname = file_requested

	# This handles the 301 if a user is looking for index.html
	# the location has moved to home.html

	########### Process 301 ###########
	if (fname == 'index.html'):

		with open('301.html', 'rb') as myfile:
			body = myfile.read()

		header = "HTTP/1.0 301 Moved Permanently\n"
		header += add_header_data(header, fname, body)
		header += "Location: http://localhost:1234/home.html\n"
		header += "Content-Type: text/html\n\n"

		send_response(connection, header, body)

	# if its not a 301 process the handle the 200/404 response
	else:
		# if the file exists in the directory open it and return the contents in the response (200, 301 responses)
		if os.path.exists(fname):		

			########### Process 200 ###########

			with open(fname, 'rb') as myfile:
				body = myfile.read()

			header = "HTTP/1.1 200 OK\n"
			header += add_header_data(header, fname, body)

			# Create the Content-Type part of header depending on file requested
			if (file_requested.endswith('.jpg')):
				content_type = 'image/jpg'
			elif (file_requested.endswith('.ico')):
				content_type = 'image/x-icon'
			elif (file_requested.endswith('.png')):
				content_type = 'image/png'
			else:
				content_type = 'text/html'

			header += "Content-Type: " + str(content_type)+'\n\n'
			send_response(connection, header, body)

		# the file requested is not found in the directory send the 404 page
		else:
			########### Process 404 ###########
			
			# open the 404 html file and store it in the body
			with open('404.html', 'rb') as myfile:
				body = myfile.read()

			header =  "HTTP/1.1 404 Not Found\n"		
			header += add_header_data(header, fname, body)
			header += "Content-Type: text/html\n\n"
			

			# combine the header and the body to form the response and it
			send_response(connection, header, body)
