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

players = []   # list of players. type :: [(Conn, Addr)]
plays = []     # plays made at some round. type :: [String, [Conn, Adr]]
num_rounds = 0 # number of game rounds


def handle_client(conn, addr):
    
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT) # blocking line of code

        if msg_length: # else: connected for the first time, no message
            msg_length = int(msg_length) # how many bytes
            msg = conn.recv(msg_length).decode(FORMAT)

            global plays
            plays.append([msg, [conn, addr]])

            # if num_rounds == 5:
            #     connected = False

    conn.close()


TIE = (-1, -1)

def handleResult(jogadaPlayer1, jogadaPlayer2):

    if jogadaPlayer1 == jogadaPlayer2:
        return TIE
    
    # return the play of who won the game
    elif jogadaPlayer1 == "rock" and jogadaPlayer2 == "scissors":
        return jogadaPlayer1
    elif jogadaPlayer1 == "rock" and jogadaPlayer2 == "paper":
        return jogadaPlayer2
    elif jogadaPlayer1 == "scissors" and jogadaPlayer2 == "paper":
        return jogadaPlayer1
    elif jogadaPlayer1 == "scissors" and jogadaPlayer2 == "rock":
        return jogadaPlayer2
    elif jogadaPlayer1 == "paper" and jogadaPlayer2 == "rock":
        return jogadaPlayer1
    elif jogadaPlayer1 == "paper" and jogadaPlayer2 == "scissors":
        return jogadaPlayer2


SLEEP_TIME = 0.1
PLAY_POS = 0
ADDR_POS = 1

def game():

    global plays
    global players
    global num_rounds

    if len(plays) == 2:
        is_game = True
    else:
        is_game = False

    if is_game:
        
        num_rounds = num_rounds + 1

        # get game result
        handleWin = handleResult(plays[0][PLAY_POS], plays[1][PLAY_POS])


        for [msg, (conn, addr)] in plays:

            print(addr)
    
            time.sleep(SLEEP_TIME) # delay for OS work

            # send result
            if handleWin != TIE:
                if msg == handleWin:
                    conn.send("You WON".encode(FORMAT))
                else:
                    conn.send("You LOSE".encode(FORMAT))
            else:
                conn.send("TIE".encode(FORMAT))
            print("result sent")
            
            time.sleep(SLEEP_TIME) # delay for OS work

            if num_rounds < 5: # allow players to do next play
                conn.send("OK".encode(FORMAT))
                print("ok sent\n")
        
        plays = []



def start(): # start the socket server

    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        total = 0
        conn, addr = server.accept() # wait (block) for a new connection to the server
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        players.append((conn, addr, total)) # add client to list of players
        conn.send("OK".encode(FORMAT)) # allows client to send messages

        active_connections = threading.active_count() - 1 # minus the start thread
        print(f"[ACTIVE CONNECTIONS] {active_connections}") 
        if active_connections == 1:
            print("Waiting for another player") # (ADD LATER) send to connected client as well
        elif active_connections == 2:
            break

    # game_end = False
    while num_rounds != 5:
        game()
        # global num_rounds
        # if num_rounds == 5: game_end = True

print("[STARTING] server is starting...")
start()
