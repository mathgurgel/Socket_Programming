from audioop import add
import socket 
import threading
import time

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind(ADDR) 

players = []   # list of players
plays = []     # plays made at some round
num_rounds = 0 # number of game rounds


def handle_client(conn, addr):
    
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT) # blocking line of code

        if msg_length: # else: connected for the first time, no message
            msg_length = int(msg_length) # how many bytes
            msg = conn.recv(msg_length).decode(FORMAT)

            # if msg == DISCONNECT_MESSAGE:
            #     connected = False
            # else:
            global plays
            plays.append([msg, [conn, addr]])

            # conn.send("Msg received".encode(FORMAT)) # send message to connected client

    conn.close()


def game_result(player1, player2, play1, play2):

    if play1 == play2:
        return (-1, -1)

    # return who won the game
    if play1 == "rock":
        if play2 == "scissors":
            return player1
        else:
            return player2
    elif play1 == "paper":
        if play2 == "scissors":
            return player1
        else:
            return player2
    else: # play1 == "scissors"
        if play2 == "paper":
            return player1
        else:
            return player2


SLEEP_TIME = 0.1
PLAY_POS = 0
ADDR_POS = 1

def game():

    global plays
    global players
    global num_rounds

    TIE = (-1, -1)

    if len(plays) == 2:
        is_game = True
    else:
        is_game = False

    if is_game:
        res_conn, res_adrr = game_result(plays[0][ADDR_POS], plays[1][ADDR_POS], plays[0][PLAY_POS], plays[1][PLAY_POS])

        for [_, (conn, addr)] in plays:
            print(addr)

            time.sleep(SLEEP_TIME) # delay for OS work
            # send result
            if (res_conn, res_adrr) != TIE:
                if addr == res_adrr:
                    conn.send("YOU WON".encode(FORMAT))
                else:
                    conn.send("YOU LOSE".encode(FORMAT))
            else:
                conn.send("TIE".encode(FORMAT))
            print("result sent")
            
            time.sleep(SLEEP_TIME) # delay for OS work
            conn.send("OK".encode(FORMAT))
            print("ok sent\n")
        
        plays = []
        num_rounds = num_rounds + 1


def start(): # start the socket server

    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept() # wait (block) for a new connection to the server
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        players.append((conn, addr)) # add client to list of players
        conn.send("OK".encode(FORMAT)) # allows client to send messages

        active_connections = threading.active_count() - 1 # minus the start thread
        print(f"[ACTIVE CONNECTIONS] {active_connections}") 
        if active_connections == 1:
            print("Waiting for another player") # (ADD LATER) send to connected client as well
        elif active_connections == 2:
            break
    
    game_end = False
    while not game_end:
        game()
        global num_rounds
        if num_rounds == 5: game_end = True

print("[STARTING] server is starting...")
start()
