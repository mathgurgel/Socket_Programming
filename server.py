import socket 
import threading
import time

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"
ALLOW_SEND = "OK"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server.bind(ADDR) 

players = []   # list of players. type :: [Int, (Conn, Addr)]
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

            if msg != DISCONNECT_MESSAGE:
                global plays
                plays.append([msg, [conn, addr]])
            else:
                connected = False

    conn.close()
    print("Connection closed\n")


TIE = "tie"

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


def incr_num_wins(winner_addr):
    
    global num_wins

    for i, [num_wins, (conn, addr)] in enumerate(players):
        if addr == winner_addr:
            players[i] = [num_wins + 1, (conn, addr)]


SLEEP_TIME = 0.1
SHOW_TIME = 2.0

PLAY_POS = 0
WINS_POS = 0
ADDR_POS = 1
CONN_POS = 0

def game_result():

    p1 = players[0]
    p2 = players[1]

    p1_num_wins = p1[WINS_POS]
    p2_num_wins = p2[WINS_POS]

    p1_conn = p1[ADDR_POS][CONN_POS]
    p2_conn = p2[ADDR_POS][CONN_POS]

    time.sleep(SLEEP_TIME) # delay for OS work

    if p1_num_wins == p2_num_wins: # tie
        p1_conn.send("Final result is a TIE!".encode(FORMAT))
        p2_conn.send("Final result is a TIE!".encode(FORMAT))
    else: 
        if p1_num_wins > p2_num_wins: # p1 won
            winner_conn = p1_conn
            loser_conn  = p2_conn
        else: # p2 won
            winner_conn = p2_conn
            loser_conn  = p1_conn

        winner_conn.send("You won the game!".encode(FORMAT))
        loser_conn.send("You lose the game!".encode(FORMAT))
    
    time.sleep(SHOW_TIME)

    for [num_wins, (conn, _)] in players:
        conn.send(f"Number of wins: {num_wins}".encode(FORMAT))
        time.sleep(SLEEP_TIME)
    time.sleep(SHOW_TIME)

    for [_, (conn, _)] in players:
        conn.send(DISCONNECT_MESSAGE.encode(FORMAT))
        print("disconnect sent\n")

def game_end():

    global players
    global num_rounds

    if num_rounds == 5:
        return True

    for [num_wins, _] in players:
        if num_wins == 3:
            return True
    
    return False

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

        count = 0 # loop counter

        for [msg, (conn, addr)] in plays:

            print(addr)

            count = count + 1

            time.sleep(SLEEP_TIME) # delay for OS work

            # send result
            if handleWin != TIE:
                if msg == handleWin:
                    incr_num_wins(addr)
                    conn.send("You WON".encode(FORMAT))
                else:
                    conn.send("You LOSE".encode(FORMAT))
            else:
                conn.send("TIE".encode(FORMAT))
            print("result sent")
            
            time.sleep(SLEEP_TIME) # delay for OS work
        
        time.sleep(SHOW_TIME)
        for [_, (conn, _)] in players:
            if not game_end():
                conn.send(ALLOW_SEND.encode(FORMAT))
                print("ok sent\n")
            else:
                is_game = False
            
        plays = []

    if game_end():
        game_result() # send match result to both clients


def start(): # start the socket server

    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept() # wait (block) for a new connection to the server
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        num_wins = 0
        players.append([num_wins, (conn, addr)]) # add client to list of players

        active_connections = threading.active_count() - 1 # minus the start thread
        print(f"[ACTIVE CONNECTIONS] {active_connections}") 
        if active_connections == 1:
            print("Waiting for another player") # (ADD LATER) send to connected client as well
            conn.send("Waiting for player".encode(FORMAT))
        elif active_connections == 2:
            for [_, (conn, _)] in players:
                conn.send(ALLOW_SEND.encode(FORMAT)) # allows clients to send messages
            break

    while not game_end():
        game()

print("[STARTING] server is starting...")
start()
