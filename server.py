from sys import exit, argv
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from select import select
from os import remove

def chat_server(port=50000, file="server.txt"):
    """Create and run a chat server on the given port. Write IP address and
    port information to the given file."""
    RECV_BUFFER = 4096 
    server = socket(AF_INET, SOCK_STREAM)
    server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    host = get_my_ip()
    server.bind((host, port))
    server.listen(10)
 
    socket_list = [server]     # list of readable connections
    message = "{}:{}\n".format(host, port)
    open(file, 'w').write(message)
    print("Chat server started: " + message)
    clients = {}  # key=addr(IP,host)  value=handle/name
 
    while True:
        # get the list of sockets which are ready to be read through select
        # 4th arg, time_out  = 0.001: return after 1 msec, reduce cpu load
        # if 4th arg time_out were 0: poll and never block; uses 100% cpu
        ready_to_read,ready_to_write,in_error = select(socket_list,[],[],0.001)
      
        for sock in ready_to_read:
            if sock == server: 
                # sock/server received a new connection request
                client, addr = server.accept()   # same as sock.accept()
                socket_list.append(client)
                clients[addr] = ""  # don't know handle yet 
                             
            # a message from a client, not a new connection
            else:
                # received message from client (on its callback port),
                # not a new connection; process and broadcast client message
                try:
                    # get a new addr here, based on sock
                    addr = sock.getpeername()
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
			# try to get name, if not already in clients dictionary
                        msg = check_msg(data.decode(), addr, clients)
                        print(msg)
                        broadcast(socket_list, server, msg)
                    else:
                        # remove the socket that's broken    
                        if sock in socket_list:
                            socket_list.remove(sock)
                        # at this stage, no data means probably connection broken
                        print("Offline1 {} {}".format(clients[addr], addr))
                        broadcast(socket_list, server,
                                  "Offline1 {} {}\n".format(clients[addr], addr))
                except:
                    print("Offline2 {} {}".format(addr, clients[addr]))
                    broadcast(socket_list, server,  
                              "Offline2 {} {}\n".format(addr, clients[addr]))
                    continue
                    
    server_socket.close()
    
def broadcast (socket_list, server, message):
    """Broadcast chat message to all clients on socket_list (including sender)."""
    for socket in socket_list:
        # send the message only to peer
        if socket != server:
            try:
                socket.send(message.encode())
            except: # broken socket connection
                socket.close()
                if socket in socket_list:
                    socket_list.remove(socket)

def get_my_ip():
    """Return my IP address, based on:
http://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    """
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("gmail.com",80))
    host = s.getsockname()[0]
    s.close()
    return host

def seq_generator(start=1):
    """Return a sequence of integers beginning with start"""
    while True:
        yield start
        start += 1

sequence = seq_generator()

def get_name(s):
    """Return any string inside square brackets in s; if
    empty, return a new guest name"""
    b1 = s.find('[')+1
    b2 = s.find(']')
    name = s[b1:b2].strip()
    if name:   
        return name
    else:
        return "guest{}".format(next(sequence))

def fix_msg(msg, name):
    """Return msg with name inserted in square brackets"""
    b1 = msg.index('[')+1
    b2 = msg.index(']')
    return msg[:b1] + name + msg[b2:]

def check_msg(msg, addr, clients):
    """Does clients have a name for this addr? If so,
    return fixed message. If not, find or make up a 
    name, return "Connected" and fixed message."""
    if clients[addr]:
        name = clients[addr]
        return fix_msg(msg, name)
    else:
        name = get_name(msg) 
        clients[addr] = name
        return "Connected {} {}\n".format(addr, name) + \
               fix_msg(msg, name)
               
 
if __name__ == "__main__":
    print("{} running".format(argv[0]))
    try:
        chat_server(file="chatserver.txt")
    except KeyboardInterrupt:
        print("You pressed ctrl-c")
        remove("chatserver.txt")

