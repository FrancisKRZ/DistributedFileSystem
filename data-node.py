###############################################################################
#
# Filename: data-node.py
#
# Description:
# 	data node server for the DFS
#
#								 hostname  port  meta-data's port
# Running:  python3 data-node.py localhost 1111  1234


from Packet import *
import sys
import socket
import socketserver
import uuid
import os

# Global Variables to help
# Data Node identify itself
# Used in acquiring and naming iNodes
host_= ''
port = ''


def usage():
	print ("""Usage: python %s <server> <port> <metadata port,default=8000>""" % sys.argv[0] )
	sys.exit(0)


def register(meta_ip, meta_port, data_ip, data_port):
	"""Creates a connection with the metadata server and
	   register as data node
	"""

	# Establish connection
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((meta_ip, meta_port))

	try:
		response = "NAK"
		sp = Packet()
		while response == "NAK":

			print("Registering")

			sp.BuildRegPacket(data_ip, data_port)
			sock.sendall(bytes(sp.getEncodedPacket(), 'UTF-8'))
			response = sock.recv(1024)

			print(response.decode())

			if response.decode() == "DUP":
				print ("Duplicate Registration")

			if response.decode() == "NAK":
				print ("Registration ERROR")

	finally:
		sock.close()


def clean_path(filename):
	str = filename.split('/')
	return str[-1]

class DataNodeTCPHandler(socketserver.BaseRequestHandler):

	def handle_put(self, p):
		"""Receives a block of data from a copy client, and 
		   saves it with an unique ID.  The ID is sent back to the
		   copy client.
		"""
		print("Data Node, handle_put")

		# name, size
		# fname, fsize, content = p.getPutFileInfo()
		fname, fsize = p.getFileInfo()


		global host_addr
		global port_num

		# We'll be creating a folder with that name
		# it'll contain file's who's name are the block id's
		# print(f"fname: {fname} , fsize: {fsize}, \ncontent: {content}")
		print(f"fname: {fname} \t fsize: {fsize}")

		# Generating unique block ID
		blockid = str(uuid.uuid1())
		blockid += ":" + host_addr + port_num

		# Sending the block ID
		self.request.sendall(bytes(blockid, 'UTF-8'))

		content = self.request.recv(1024)
		print(f"\nContent's len: {len(content)}\n fsize: {fsize}\n")

		while(len(content) < fsize):
			content += self.request.recv(1024)
			print(f"\nWriting... {len(content)}\n")


		print("Writing done...")
		# print(f"\nContent Received: {content}\n")

		print(f"blockid: {blockid}")


		print("Cleaning Path...")
		fname = clean_path(fname)
		dir_name = fname

		print(f"Directory Name to make: {dir_name}")

		if not os.path.exists( dir_name ):

			print("making...")
			os.makedirs( dir_name )

		# else:
		# 	print("It already exists goober!")

		# Now we'll create files
		# containing the content
		# IDs: the blockid's in order
		write_to_file_path = dir_name + "/" + blockid
		print(f"\nWrite to file: {write_to_file_path}")

		# Writes with wb
		write_to_file = open(write_to_file_path, 'wb')
		write_to_file.write(content)
		write_to_file.close()

		print("\nFinished Writing To\n")



	def handle_get(self, p):
		
		print("Data Node, handle_get")

		# Get the block id from the packet
		fname = p.getFileName()
		print(f"fname: {fname}")

		blockIDs = os.listdir(fname)
		sorted_IDs = sorted(blockIDs)
		print(sorted_IDs)

		# print(f"Who am I? {host_addr} {port_num}")

		node_addr = host_addr + '' + port_num
		node_inode = ''
		for i in sorted_IDs:
			if node_addr in i:
				node_inode = i


		print(f"This is my inode {node_inode}")

		# Reads with rb
		with open(os.path.join(fname, node_inode), 'rb') as f:
			data = f.read()
			print(f"\n\nData Read: {data}")
			self.request.sendall(data)


		print("\nFinished getting\n")


	def handle(self):
		msg = self.request.recv(1024)
		print("handle -- data-note.py")
		print (msg, type(msg))

		p = Packet()
		p.DecodePacket(msg)

		cmd = p.getCommand()
		if cmd == "put":
			self.handle_put(p)

		elif cmd == "get":
			self.handle_get(p)
		

if __name__ == "__main__":

	META_PORT = 8000
	if len(sys.argv) < 4:
		usage()

	# try:
	HOST = sys.argv[1]
	PORT = int(sys.argv[2])
	# DATA_PATH = sys.argv[3]

	# print(f"HOST {HOST} PORT {PORT} DATA_PATH {DATA_PATH}")

	global host_addr 
	host_addr = HOST
	global port_num  
	port_num = str(PORT)

	if len(sys.argv) > 3:
		META_PORT = int(sys.argv[3])
		print(f"META_PORT {META_PORT}")

	# if not os.path.isdir(DATA_PATH):
	# 	print ("Error: Data path %s is not a directory." % DATA_PATH)
	# 	usage()
	# except:
		# usage()

	register("localhost", META_PORT, HOST, PORT)
	server = socketserver.TCPServer((HOST, PORT), DataNodeTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
	server.serve_forever()
