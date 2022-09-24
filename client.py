import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT) # encode the string to bytes
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT) # first send size of the message
    send_length += b' ' * (HEADER - len(send_length)) # make sure it is 64 bytes
    client.send(send_length)
    client.send(message)

while True:
    msg = client.recv(HEADER).decode(FORMAT) # receive message from server
    print(msg)
    if msg == "OK":
        play = input("Play: ")
        send(play)


