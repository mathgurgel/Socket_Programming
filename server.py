import socket 
import threading

# message handling > separate threads for each client
# client does not need to wait for the other one to comunicate with the server

# 64 bytes
HEADER = 64 # tells the size of the message which comes next
PORT = 5050 # above 4000
SERVER = socket.gethostbyname(socket.gethostname()) # gets ipv4 by name (local network)
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# af = family. inet > type of ip adress (ipv4)
# streaming data through the socket (standart way of sending data)
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # open device to other connections
server.bind(ADDR) # binds the server to the address
# anything that connects to ADDR will hit the socket

# run in parallel
def handle_client(conn, addr): # connections between client and server
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        # header: how many bytes we want to receive from client
        msg_length = conn.recv(HEADER).decode(FORMAT) # blocking line of code
        # not pass this ^ line of code til we receive a message from our client
        if msg_length: # else: connected for the first time, no message
            msg_length = int(msg_length) # how many bytes
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            conn.send("Msg received".encode(FORMAT)) # send message to connected client

    conn.close()
        

def start(): # start the socket server
    server.listen() # listening to new connections
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        # conn = object (socket) (what we are connecting)
        conn, addr = server.accept() # wait (block) for a new connection to the server
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        # number of client connections
        print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1}") # minus the start thread


print("[STARTING] server is starting...")
start()

