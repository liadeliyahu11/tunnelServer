"""
Liad's Simple tunnel server - wrote for horesh's project.
You have done a really good job you should be proud of your project - i am serious!
"""
import time
import sys
import socket
import select

MAX_BUFFER_SIZE = 2048
LISTEN_MAX = 15
LOCAL_SERVER_IP = "127.0.0.1"
LOCAL_PORT = 8000
SELF_SOCKET = ("0.0.0.0", 80)
FORWARD_SOCKET = (LOCAL_SERVER_IP, LOCAL_PORT)

class Forwarder:
    def __init__(self):
        self.forward_socket = socket.socket()

    def run(self, server, port):
    	# create new connection with the local server(the one you should protect)
        try:
            self.forward_socket.connect((server, port))
            return self.forward_socket
        except Exception, ex:
            print ex

class TheServer:
    input_list = []
    tunnels = {}

    def __init__(self):
    	# create new socket for the server
        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(SELF_SOCKET)
        self.server.listen(LISTEN_MAX)

    def main_loop(self):
    	"""
		The main function handle(send and receive) the clients data.
    	"""
    	# add the server to the sockets list
        self.input_list.append(self.server)
        
        while True:
        	# this line checking all the sockets - which one wait for data or which already send its data
            inputready, outputready, exceptready = select.select(self.input_list, [], [])
            
            for self.sock in inputready:
               	if self.sock == self.server: # case it is the server - get new connection
                    self.on_accept()
                    break

                # if not - get data from user
                self.data = self.sock.recv(MAX_BUFFER_SIZE) 
                
                if len(self.data) == 0: # if no data close the connection
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
    	"""
		Accept new client to the forwarding system.
    	"""
        forward = Forwarder().run(FORWARD_SOCKET[0], FORWARD_SOCKET[1]) # create new local server connection
        
        clientsock, clientaddr = self.server.accept()
        
        #connect the client and the server together
        if forward:
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.tunnels[clientsock] = forward
            self.tunnels[forward] = clientsock
            print clientaddr, "- new connection !"
        else:
            print "Can't establish connection with server.",
            print "Closing connection with ", clientaddr
            clientsock.close()

    def on_close(self):
    	"""
		Close the connection with the client and the local server
    	"""
        print self.sock.getpeername(), " - left"
        
        self.input_list.remove(self.sock)
        self.input_list.remove(self.tunnels[self.sock])
        out = self.tunnels[self.sock]
       	
        self.tunnels[out].close()
        
        self.tunnels[self.sock].close()
        
        del self.tunnels[out]
        del self.tunnels[self.sock]

    def on_recv(self):
    	"""
		Get the data from the user and forward to second side.
		And this function calls the FILTER FUNCTION that is the most important thing. 
    	"""
        data = self.data
        # noTE FOR HORESH : here you should call your filter function on the data!
        print data
        self.tunnels[self.sock].send(data)

if __name__ == '__main__':
        server = TheServer()
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "Ctrl C pressed - server stoped"
            sys.exit(1)
