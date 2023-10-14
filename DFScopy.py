
###############################################################################
#
# Filename: DFScopy.py
#
# Description:

# This is a client-side Python script that can be used to 
# copy a file to or from the distributed file system (DFS). 

# The file system is accessed through a metadata server, 
# which is specified by the IP address and port number 
# passed as command line arguments when running the script. 

# The script can be used to either copy a file from the local file system to the DFS, 
# or from the DFS to the local file system.

# When the server receives a PUT request from a client, it receives a block of data, 
# generates a unique identifier for the block, and saves the data with the identifier. 
# The server then sends the identifier back to the client. 

# When the server receives a GET request from a client, 
# it retrieves the requested file from its data path and sends it to the client. 



# ----------- How to Run ------------  

# Copying from: 
# We want to know which file we want to copy from the DFS
# and where we'll be copying.
#								server:port:file_name  /our/machines/directory/file
# Run in terminal:  python3 DFScopy.py localhost:1234:pajaro.jpg /home/User/pajaro.jpg


# Copying to: 
# Note, we do not need to specify DFS' directory, data-node takes care of it.
# We want to know which file we want to copy and where to copy it to
# You may use ls.py to see which available files we can copy

# Run in terminal: python3 DFScopy.py ~/path/Pingu.txt localhost:1234


import socket
import sys
import os.path
from Packet import *

def usage():
	print ("""
	Usage:\n\tFrom DFS: python %s <server>:<port>:<dfs file path> <destination file>
	\n\tTo DFS: python %s <source file> <server>:<port>:<dfs file path>
	""" % (sys.argv[0], sys.argv[0]) )
	sys.exit(0)

# getDataChunks divides a given data 
# string into a specified number of equal-sized chunks.
def getDataChunks(data, data_nodes):

	chunks = []
	# Calculate the amount of data per node
	data_per_node = len(data) // data_nodes

	# Iterate over the data nodes and create the chunks
	for i in range(data_nodes):
		# Calculate the start and end indices of the current chunk
		start = i * data_per_node
		end = start + data_per_node
		
		# Create the chunk and append it to the list
		chunk = data[start:end]
		chunks.append(chunk)

	# Check if the sum of the lengths of the chunks is less than the
	# length of the data. If so, add the remaining data to the last chunk.
	len_sum = sum(len(chunk) for chunk in chunks)
	if len_sum < len(data):
		remainder = len(data) - len_sum
		chunks[-1] += data[-remainder:]

	return chunks


# The copyToDFS function is used to copy a file 
# from the local file system to the DFS. 
# It establishes a connection to the metadata server, 
# reads the contents of the file to be copied, 
# and sends a put request packet to the 
# server along with the file name and size. 
# The metadata server responds with a 
# list of data nodes where the file will be stored, 
# and the copyToDFS function divides the file 
# contents into equal-sized chunks and sends them to the data nodes. 
def copyToDFS(address, fname):

	# Create a connection to the metadata server
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sp = Packet()
	# Address
	ip, port = address

	# Read file
	# Reads as rb
	file = open(fname, 'rb')	
	file_contents = file.read()
	fsize = os.path.getsize(fname)


	# Connect
	sock.connect((ip, port))
	# Create a Put packet with the fname and the length of the data,
	# and sends it to the metadata server
	sp.BuildPutPacket(fname, fsize)
	sock.sendall(bytes(sp.getEncodedPacket(), 'UTF-8'))
	rec = sock.recv(1024).decode('UTF-8')

	# sp.DecodePacket(rec)

	if rec == "DUP":
		print("Duplicate!")
		exit()
	else:
		sp.DecodePacket(rec)

	dataNodes = sp.getDataNodes()
	# pair, address : odd , port
	nodes = []
	for addr, port in dataNodes:
		print(f"Address: {addr} Port: {port}")
		nodes.append( (addr, port) )
	
	print(f"Nodes: {nodes} \nNodes Len: {len(nodes)}")


	# ---------------------- Setting Up To Send Data Contents  --------------

		# ---------------------- First Splicing in Chunks  --------------

	data_chunks = getDataChunks(file_contents, len(nodes))
	# print(f"\nData_Chunks\n{data_chunks}\n")

		# -----------------                               --------------

	# Content from the file (file_contents), 
	# prepared to be put in a packet. WORK-IN-PROGRESS

	# List of Sockets to send file content(s) to Node(s)
	send_contents_to_DN = [None] * len(nodes)
	save_node_IDs 		= [None] * len(nodes)

	for i in range(len(nodes)):

		sp.BuildPutPacket(fname, len(data_chunks[i]))

		# print(f"Working on Node: {nodes[i]}")
		# Connecting to the node
		send_contents_to_DN[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print(f"Connecting to Node: {send_contents_to_DN[i]}")

		send_contents_to_DN[i].connect(nodes[i])
		
		# Sending the data to the Node(s)
		send_contents_to_DN[i].sendall(bytes(sp.getEncodedPacket(), 'UTF-8'))
		save_node_IDs[i] = send_contents_to_DN[i].recv(1024).decode('UTF-8')
		send_contents_to_DN[i].sendall(data_chunks[i])
		
		print(f"Response after connecting to Data Node: \
		{type(save_node_IDs[i])} {save_node_IDs[i]}\n")

	# ---------------------- Finishing Confirm Data Read --------------
	print("-----------------------------------------------------")



# The copyFromDFS function is used to 
# copy a file from the DFS to the local file system. 
# It establishes a connection to the metadata server, 
# sends a get request packet with the file name and size, 
# and receives the file contents from the data nodes. 
# It then writes the contents to a file in the local file system.
def copyFromDFS(address, fname, path):

	# Create a connection to the data server	
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sp = Packet()
	print(f"fname: {fname} \n path: {path}")

	# Address and Connection
	ip, port = address
	sock.connect((ip, port))

   	# Contact the metadata server to ask for information of fname
	sp.BuildGetPacket(fname)
	sock.sendall(bytes(sp.getEncodedPacket(), 'UTF-8'))
	rec = sock.recv(1024).decode()
	sp.DecodePacket(rec)

	fname, fsize = sp.getFileInfo()
	# print(f"fsize: {fsize}")

	# Make a list of data-node addresses
	dataNodes = sp.getDataNodes()
	# pair, address : odd , port
	nodes = []
	for addr, port in dataNodes:
		print(f"Address: {addr} Port: {port}")
		nodes.append( (addr, port) )
	
	print(f"Nodes: {nodes}")
	size_per_nodes = fsize // len(nodes)

	# File entry
	# Writes with append binary
	file = open(path, 'ab+')

	# ---------------------- Setting Up To Send Data Contents  --------------
	# Content from the file (file_contents), 
	# prepared to be put in a packet. WORK-IN-PROGRESS
	# List of Sockets to send file content(s) to Node(s)
	send_contents_to_DN = [None] * len(nodes)
	save_node_content 	= [None] * len(nodes)

	for i in range(len(nodes)):

		sp.BuildGetPacket(fname)
		print(f"Working on Node: {nodes[i]}")
		# Connecting to the node
		send_contents_to_DN[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print(f"Connecting to Node: {send_contents_to_DN[i]}")

		send_contents_to_DN[i].connect(nodes[i])
		
		# Sending the data to the Node(s)
		send_contents_to_DN[i].sendall(bytes(sp.getEncodedPacket(), 'UTF-8'))
		# If there is no error response Retreive the data blocks
		# save_node_content[i] = send_contents_to_DN[i].recv(1024).decode('UTF-8')

		save_node_content[i] = send_contents_to_DN[i].recv(1024)
		node_chunk = save_node_content[i]

		print(f"\n{len(node_chunk)} \t fsize: {fsize}")
		while( len(node_chunk) < size_per_nodes):
			node_chunk += send_contents_to_DN[i].recv(1024)
			# print(f"Chunk Received: {node_chunk}")
			print(f"Chunk Received: {len(node_chunk)} \
				\t Total Chunk Size: {size_per_nodes}")


		print(f"\nSave Node Content {i} \t{len(save_node_content[i])}")
		# print(f"\nSaving the whole chunk: {len(node_chunk)}")
		# Save the file's content
		file.write(node_chunk)
		print(f"Response after connecting to Data Node: \
			{type(save_node_content[i])} {save_node_content[i]}\n")



	file.close()

	# ---------------------- Finishing Confirm Data Read --------------
	print("-----------------------------------------------------")

# parses the command line arguments to 
# determine the copy mode and extract 
# the necessary information such as 
# the metadata server address, file name, and file path. 
# It then calls the appropriate main function for the copy operation.
if __name__ == "__main__":
	if len(sys.argv) < 3:
		usage()

	file_from = sys.argv[1].split(":")
	file_to = sys.argv[2].split(":")

	if len(file_from) > 1:
		ip = file_from[0]
		port = int(file_from[1])
		from_path = file_from[2]
		to_path = sys.argv[2]

		if os.path.isdir(to_path):
			print("Error: path %s is a directory.  \
				Please name the file." % to_path)
			usage()

		copyFromDFS((ip, port), from_path, to_path)

	# elif len(file_to) > 2:
	else:
		ip = file_to[0]
		port = int(file_to[1])
		from_path = sys.argv[1]

		if os.path.isdir(from_path):
			print("Error: path %s is a directory.  \
				Please name the file." % from_path)
			usage()

		# Note, we just specify what file we
		# want to copy and the function
		# takes care of the rest 
		# (communicating to DFS to save it with it)
		copyToDFS((ip, port), from_path)
