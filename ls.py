###############################################################################
#
# Filename: ls.py
#
# Description:
# This is a client-side Python script that contacts a metadata server and asks for a list of files. 
# The metadata server is specified by the IP address 
# and port number passed as command line arguments 
# when running the script. 

# The client sends a list request packet to the server 
# and receives a response with a list of files in the form of a string. 

# The string is processed to extract the names and sizes 
# of the files and print them to the console.

# -------------- How to Run ---------------
# 			    server:port
# python3 ls.py localhost:1234

import socket
import sys
from Packet import *

# The stripString function processes the list response string 
# by removing various 'junk' characters such as curly braces and colons, 
# and splitting the string into a list of file #names and sizes. 
# The client function establishes a connection to the metadata server using a socket, 
# sends the list request packet, and receives the list response string. 
# It then processes the response string and prints the names and sizes of the files to the console. 
def stripString(str):

	listRec = str
	listRec = listRec.replace('{', '')
	listRec = listRec.replace('}', '')
	listRec = listRec.replace('[', '')
	listRec = listRec.replace(']', '')
	listRec = listRec.replace(':', '')
	listRec = listRec.replace('files', '')
	listRec = listRec.replace('"', '')
	listRec = listRec.split(',')

	return listRec


def usage():
	print ("""Usage: python %s <server>:<port, default=8000>""" % sys.argv[0] )
	sys.exit(0)

# The client function establishes a connection to the metadata server using a socket,
# sends the list request packet, and receives the list response string.
# It then processes the response string using the stripString function
# and prints the names and sizes of the files to the console.
def client(ip, port):
	
	# Create the socket and packet
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sp = Packet()

	# Connects to the Socket / Server
	# and build a list packer
	sock.connect((ip, port))
	sp.BuildListPacket()

	# Sends the build request packet
	sock.sendall(bytes(sp.getEncodedPacket(), 'UTF-8'))
	# Receive the packet :D
	rec = sock.recv(1024).decode()

	# Clean the response!
	listRec = stripString(rec)
	listLen = len(listRec)

	# Prints out the given request :)
	for i in range(0, listLen-1, 2):

		msg = listRec[i] + listRec[i+1]
		print(f"{msg} bytes")

	sock.close()


# If the script is run as the main module, 
# it parses the command line arguments to extract the 
# IP address and port number of the metadata server. 
# If the port number is not provided, it defaults to 8000. 
# The script then calls the client function to contact 
# the metadata server and request the list of files.
if __name__ == "__main__":

	if len(sys.argv) < 2:
		usage()

	ip = None
	port = None 

	server = sys.argv[1].split(":")
	if len(server) == 1:
		ip = server[0]
		port = 8000
	elif len(server) == 2:
		ip = server[0]
		port = int( server[1] )

	if not ip:
		usage()


	client(ip, port)
