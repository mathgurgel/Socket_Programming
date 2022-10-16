import socket
import tkinter as tk
import threading
import pygame
import button
from sys import exit
import time

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"
ALLOW_SEND = "OK"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
allow_button = False
game_end = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):

    message = msg.encode(FORMAT) # encode the string to bytes
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT) # first send size of the message
    send_length += b' ' * (HEADER - len(send_length)) # make sure it is 64 bytes
    client.send(send_length)
    client.send(message)


def pygame_gui():

    global allow_button

    #create display window
    SCREEN_HEIGHT = 500
    SCREEN_WIDTH = 800

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Button Demo')

    #load button images
    rock_img = pygame.image.load('graphics/rockbtt.png').convert_alpha()
    paper_img = pygame.image.load('graphics/paperbtt.png').convert_alpha()
    scr_img = pygame.image.load('graphics/scrbtt.png').convert_alpha()

    #create button instances
    rock_button = button.Button(100, 200, rock_img, 1)
    paper_button = button.Button(300, 200, paper_img, 1)
    scr_button = button.Button(500, 200, scr_img, 1)

    #game loop
    run = True
    while run:

        screen.fill((202, 228, 241))

        if allow_button:
            
            # draw buttons
            rock_button.draw(screen)
            paper_button.draw(screen)
            scr_button.draw(screen)
            
            if rock_button.was_clicked():
                send("rock")
                allow_button = False
            if paper_button.was_clicked():
                send("paper")
                allow_button = False
            if scr_button.was_clicked():
                send("scissors")
                allow_button = False

        #event handler
        for event in pygame.event.get():
            #quit game
            if event.type == pygame.QUIT:
                run = False

        if game_end:
            run = False

        pygame.display.update()

    pygame.quit()
    exit()


thread = threading.Thread(target=pygame_gui)
thread.start()
print("interface started\n")

while True:
    msg = client.recv(HEADER).decode(FORMAT) # receive message from server
    print(msg)
    if msg == ALLOW_SEND:
        allow_button = True
    elif msg == DISCONNECT_MESSAGE:
        game_end = True
        send(msg) # warn handle_client to end connection
        break