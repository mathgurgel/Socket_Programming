import socket
import tkinter as tk
import threading
import pygame
import button

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"
ALLOW_SEND = "OK"
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


def pygame_gui():

    #create display window
    SCREEN_HEIGHT = 500
    SCREEN_WIDTH = 800

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Button Demo')

    #load button images
    start_img = pygame.image.load('graphics/start_btn.png').convert_alpha()
    exit_img = pygame.image.load('graphics/exit_btn.png').convert_alpha()

    #create button instances
    start_button = button.Button(100, 200, start_img, 0.8)
    exit_button = button.Button(450, 200, exit_img, 0.8)

    #game loop
    run = True
    while run:

        screen.fill((202, 228, 241))

        if start_button.draw(screen):
            print('START')
        if exit_button.draw(screen):
            print('EXIT')

        #event handler
        for event in pygame.event.get():
            #quit game
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update()

    pygame.quit()


def game_interface():
    top = tk.Tk()
    top.mainloop()

thread = threading.Thread(target=pygame_gui)
thread.start()

print("hello")

while True:
    msg = client.recv(HEADER).decode(FORMAT) # receive message from server
    print(msg)
    if msg == ALLOW_SEND:
        play = input("Play: ")
        send(play)
    elif msg == DISCONNECT_MESSAGE:
        send(msg) # warn handle_client to end connection
        break

pygame.quit()