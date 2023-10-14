###############################################################################
#
# Filename: meta-data.py
#
# Description:
# This is a Python program that implements a metadata server for a distributed file system (DFS) project. 

# The server listens for incoming requests from clients and responds with the appropriate action. 
# The server uses the mds_db library to interact with a MySQL database, 
# which stores information about the data nodes and files in the DFS. 

# The server supports four types of requests: 
# REGISTER, which registers a new data node with the server; 
# LIST, which retrieves a list of files from the database and sends it to the client; 
# PUT, which inserts a new file into the database and sends data nodes to save the file; 
# GET, which retrieves a file from the DFS and sends it to the client. 

# The server uses the Packet class to encode and decode packets for communication with the clients. 
# The program can be run by passing a port number as an argument, 
# with a default value of 8000 if no argument is provided.

# 					by default localhost port
# Running:  python3 meta-data.py 1234


from mds_db import *
from Packet import *
import sys
import socketserver

def usage():
	print ("""Usage: python %s <port, default=8000>""" % sys.argv[0] )
	sys.exit(0)


def clean_path(filename):
	str = filename.split('/')
	return str[-1]

class MetadataTCPHandler(socketserver.BaseRequestHandler):

	def handle_reg(self, db, p):
		"""Register a new client to the DFS  ACK if successfully REGISTERED
			NAK if problem, DUP if the IP and port already registered
		"""
		addr = p.getAddr()
		port = p.getPort()
		
		print("Handle Register!")
		print(f"addr: {addr}")
		print(f"port: {port}")

		# Check if the Data Node is already registered
		# Replies with the appropiate response:
		# ACK -- Sucessful
		# DUP -- Duplicate
		# NAK -- Failure
		if (addr, port) not in db.GetDataNodes():
			db.AddDataNode(addr, port)
			self.request.sendall(bytes("ACK", 'UTF-8'))
			print(f"Available Nodes: {db.GetDataNodes()}")
		elif (addr, port) in db.GetDataNodes():
			self.request.sendall(bytes("DUP", 'UTF-8'))
		else:
			self.request.sendall(bytes("NAK", 'UTF-8'))


	# The Client's ls.py executes the following which 
	# returns a list of files from the database
	def handle_list(self, db):
		"""Get the file list from the database and send list to client"""

		# print("Inside Handle List!")
		sp = Packet()

		sp.BuildListResponse(db.GetFiles())
		self.request.sendall(bytes(sp.getEncodedPacket(), 'UTF-8'))
		print("Handle List -- Request Sent!")


	# If it's Copy's putTo will check if it's already
	# in the Database, else it'll insert it to the database
	def handle_put(self, db, p):
		"""Insert new file into the database and send data nodes to save
		   the file.
		"""

		print("Getting File Info from Packet!")
		fname , fsize = p.getFileInfo()

		# print(f"fname: {fname} fsize: {fsize}")
		# print(f"getFiles {db.GetFiles()}")

		# check with if fname and fsize in db.GetFiles() lol
		# Check if duplicated already
		if len(db.GetFiles()) > 0 and fname in list(zip(*db.GetFiles()))[0]:
			self.request.sendall(bytes("DUP", 'UTF-8'))

		# If they're not, sends packet(s) to the Data Node(s)
		# to copy the file to the DFS
		else:
			# print("Building!")
			p.BuildPutResponse(db.GetDataNodes())
			self.request.sendall(bytes(p.getEncodedPacket(), 'UTF-8'))
			# print("Inserting!")
			print(f"\nInserting File ({fname}, {fsize})\n")
			fname = clean_path(fname)
			# print(f"\nClean Path ({fname})\n")
			db.InsertFile(fname, fsize)


	# Copy's getFrom DFS will verify if it exists
	# then shall send packet(s) to the Data Node(s)
	# to copy the file from the DFS 
	# to the client's specified >file< path
	def handle_get(self, db, p):
		"""Check if file is in database and (then?) return list of
			server nodes that contain the file.
		"""

		fsize, fInfo = db.GetFileInode( p.getFileName() )
		# print(f"fsize: {fsize}")

		# -- Working -- 
		print(db.GetDataNodes())
		# Temporary Solution
		p.BuildGetResponse( db.GetDataNodes() , fsize )
		
		# For some unknown reason, this doesn't works :(
		# fname, fsize = p.getFileInfo()
		# print(f"name: {fname} fsize: {fsize}")

		self.request.sendall(bytes(p.getEncodedPacket(), 'UTF-8'))
		fname, fsize = p.getFileInfo()		

		# -- End of Working

	# Here we handle which packet request
	# we're receiving :)		
	def handle(self):

		print("Waiting for instructions...")
		# Establish a connection with the local database
		db = mds_db("dfs.db")
		db.Connect()

		# Define a packet object to decode packet messages
		p = Packet()

		# Receive a msg from the list, data-node, or copy clients
		msg = self.request.recv(1024)
		# print("handle()")
		print (msg, type(msg))
		
		# Decode the packet received
		p.DecodePacket(msg)
		# print(f"PACKET: {p}")

		# Extract the command part of the received packet
		cmd = p.getCommand()
		addr = p.getAddr()
		port = p.getPort()

		print(f"ADDR: {addr} , PORT: {port} , CMD: {cmd}")

		# Invoke the proper action 
		if   cmd == "reg":
			# Registration client
			print("registering")
			self.handle_reg(db, p)


		elif cmd == "list":
			# Client asking for a list of files
			print("listing")
			self.handle_list(db)


		elif cmd == "put":
			# Client asking for servers to put data
			print("putting")
			self.handle_put(db, p)


		elif cmd == "get":
			# Client asking for servers to get data
			print("getting")
			self.handle_get(db, p)


		db.Close()

if __name__ == "__main__":
	HOST, PORT = "", 8000

	if len(sys.argv) > 1:
		try:
			PORT = int(sys.argv[1])
		except:
			usage()

	server = socketserver.TCPServer((HOST, PORT), MetadataTCPHandler)

	# Activate the server; this will keep running until you
	# interrupt the program with Ctrl-C
	server.serve_forever()
