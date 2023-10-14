--------------------------                      --------------------------

                            Operating Systems

                Project 3 - Distributed File System


-------------------------- Program Description: --------------------------


    In this project the student will implement the main components of a file system 
    by implementing a "simple", yet functional, distributed file system (DFS).

    A distributed file system (DFS) is a type of file system that allows users to access 
    and store data on multiple servers in a network, rather than on a single, dedicated server. 
    It allows users to access and manage files as if they were all stored locally, 
    while still providing the benefits of storing data on multiple servers, 
    such as increased storage capacity, improved data reliability and availability, 
    and better performance. In a DFS, the file system software is responsible 
    for managing the data stored on the servers and providing users with transparent access to the data. 

    The project will implement the DFS with the following workings
    inodes, and data blocks.

    This project was updated to utilize Python 3.
    You are able to send and receive most type of files.
    Not verified: video files, sound files.


--------------------------                     --------------------------

-------------------------- How To Run --------------------------

    TLDR:
        Run meta server first:
            python3 meta-data.py 1234
        Then run the Data Node(s):
            python3 data-node.py localhost 1111 1234
    
        Finally the client(s) // Copy or ls:
            Copying to the DFS:
                python3 DFScopy.py ~/src_path/Pingu.c localhost:1234
            Copying from the DFS:
                python3 DFScopy.py localhost:1234:Pingu.c /home/User/dst_path/Penguin.c
            Listing Files in ls:
                python3 ls.py localhost:1234


    > Note <
    We take out some required command line arguments
    as some are paths that are taken care of by Data Node(s)
    or other aspects


    ---------------- Data Base Creation ----------
    First and forthmost!
    
    We've to make sure a fresh database is present,
    accomplished by running python3 createdb.py


    ---------------             -----------------

    ---------------- Server Side ----------------
    1) For the emulation, we need a running meta-data server,

    Format:
        python3 meta-data.py ;port, default=8000;
    Example:
        python3 meta-data.py 1234


    2) Then we need Data Node(s) to be able to store and copy file's to and from:

    Format:
        python3 data-node.py ;server address; ;port; ;metadata port,default=8000;
    Example:
        python3 data-node.py localhost 1111  1234

    
    ----------------             ----------------

    ---------------- Client Side ----------------
    The Client side is the regular User(s)
    They can either list the file(s) in the DFS
    or copy their files from and to the DFS



    The list client just sends a list request to the 
    meta data server and then waits for a list of file names with their size.

    Listing file(s):

    Note about server and port parameters:
        Where server is the metadata server IP and port is the metadata server port.  
        If the default port is not indicated the default port is 8000 and no ':' character is necessary.

    Format:
       python3 ls.py ;server;:;port, default=8000;
    Example:
        python3 ls.py localhost:1234

    Expected output:

        projecto_final.asm 256 bytes
        iceberg.txt 200 bytes
        Camarones.deb 4 bytes


    Copying file(s):

        Note about the server and port parameters:
            Server address is the meta data server address, port is the data-node port number, 
            data path is a path to a directory to store the data blocks, 
            and metadata port is the optional metadata port if it was ran in a different port other than the default port.

        * Copy to the DFS:
            
            Format:
                python3 copy.py ;source file path; ;server;:;port;
            Example:
                python3 DFScopy.py ~/src_path/penguin.txt localhost:1234

                -> NOTE <-
                DFS File Path Is NOT needed!
                Please execute as specified
                Data Node takes care of saving to DFS path

        * Copy from the DFS:

            Format:
                python copy.py ;server;:;port;:;dfs file name; ;destination file path;
            Example:
                python3 DFScopy.py localhost:1234:penguin.txt /home/User/destination.txt


    --------------------------
    Video Demonstration:
        https://youtu.be/fJgE55gr6Bk
    --------------------------


    --------------------------           --------------------------

                Specific Details about our DFS emulation's instructions:


    About the Meta Server:

        The meta data server containst the metadata (inode) information of the files in your file system.  
        It will also keep registry of the data servers that are connected to the DFS.

    About the Data Node(s):

        The data node is the process that receives and saves the data blocks of the files. 
        It must first register with the metadata server as soon as it starts its execution. 
        The data node receives the data from the clients when the client wants to write a file, 
        and returns the data when the client wants to read a file.

        Listen to writes (puts):

            The data node will receive blocks of data, store them using and unique id, and return the unique id.
            Each node must have its own blocks storage path.  You may run more than one data node per system.

        Listen to reads (gets):

            The data node will receive request for data blocks, and it must read the data block, and return its content.


--------------------------           --------------------------




--------------------------           --------------------------


References & Resources used:

    [Official Resources]:
    
        Modern Operating System 4th Ed by Tanenbaum

        Python SocketServer library: for the socket communication.
            https://docs.python.org/2/library/socketserver.html

        uuid: to generate unique IDs for the data blocks
            https://docs.python.org/2/library/uuid.html

            Libraries for json encoding and sql Data Base
            https://docs.python.org/2/library/json.html
            https://docs.python.org/2/library/sqlite3.html
        
    [Unofficial Resources]:
    
        Python String | replace()
        https://www.geeksforgeeks.org/python-string-replace/
    
        How to get file extension in Python?
        https://www.geeksforgeeks.org/how-to-get-file-extension-in-python/

        Python – Divide String into Equal K chunks
        https://www.geeksforgeeks.org/python-divide-string-into-equal-k-chunks/


    Please have mercy... :'(
                        __
                     -=(o '.
                        '.-.\
                        /|  \\
                        '|  ||
                         _\_):,_
_____________________________________________________
# DFS
# DFS
