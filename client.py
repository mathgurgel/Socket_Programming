import socket
import threading
import pygame
import button
from sys import exit

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "DISCONNECT"
ALLOW_SEND = "OK"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
MUSIC_VOLUME = 0.5
allow_button = False
game_end = False
new_display_msg = False
recv_msg = ""
display_logo = True

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

    pygame.init()

    global allow_button
    global new_display_msg
    global recv_msg
    global display_logo

    # create display window
    SCREEN_WIDTH = 640
    SCREEN_HEIGHT = 480

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('JO-KEN-PO')
    bg = pygame.image.load('graphics/bg.png').convert_alpha()
    bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

    game_logo = pygame.image.load('graphics/logo.png').convert_alpha()
    game_logo_rect = game_logo.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))

    # load button images
    rock_img = pygame.image.load('graphics/rock.png').convert_alpha()
    paper_img = pygame.image.load('graphics/paper.png').convert_alpha()
    scr_img = pygame.image.load('graphics/scissors.png').convert_alpha()

    # create button instances
    rock_button = button.Button(SCREEN_WIDTH / 5, SCREEN_HEIGHT / 2, rock_img, 0.15)
    paper_button = button.Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, paper_img, 0.15)
    scr_button = button.Button(SCREEN_WIDTH - (SCREEN_WIDTH / 5), SCREEN_HEIGHT / 2, scr_img, 0.15)

    # load fonts
    main_font = pygame.font.Font('font/Karate.ttf', 50)
    snd_font = pygame.font.Font('font/dogica.ttf', 20)

    # play music
    bg_music = pygame.mixer.Sound('audio/jojo.mp3')
    bg_music.play(loops = -1)
    bg_music.set_volume(MUSIC_VOLUME)

    # game loop
    run = True
    while run:

        screen.fill((202, 228, 241))
        screen.blit(bg, (0, 0))

        if display_logo:
            
            screen.blit(game_logo, game_logo_rect)

            hit_space = snd_font.render("Hit space to play...", False, (255, 255, 255))
            hit_space_rect = hit_space.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - (SCREEN_HEIGHT / 8)))
            screen.blit(hit_space, hit_space_rect)

        elif allow_button:

            new_display_msg = False # already displayed

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

        elif new_display_msg:

            display_msg = main_font.render(recv_msg, False, (255, 255, 255))
            display_msg_rect = display_msg.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(display_msg, display_msg_rect)
        
        else:

            wait_msg = main_font.render("Wait...", False, (255, 255, 255))
            wait_msg_rect = wait_msg.get_rect(center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            screen.blit(wait_msg, wait_msg_rect)

        # event handler
        for event in pygame.event.get():
            # quit game
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    display_logo = False

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
    else:
        recv_msg = msg
        new_display_msg = True