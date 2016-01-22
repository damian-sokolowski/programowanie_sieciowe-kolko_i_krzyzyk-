# coding=utf-8
from socket import *
import pickle
import pygame
import sys
from pygame.locals import *


def init_window(width_box, height_box):
    bg_color = (255, 255, 255)
    window = pygame.display.set_mode((width_box * 3, height_box * 3), 0, 32, )
    pygame.display.set_caption('Kółko i krzyżyk', )
    window.fill(bg_color, )
    draw_boards(window, width_box, height_box, )
    pygame.display.flip()
    return window


def draw_boards(game_window, width_box, height_box, ):
    bg_color = (0, 0, 0)
    for i in range(1, 3):
        pos_x, pos_y = ((width_box * i), (height_box * i))
        pygame.draw.line(game_window, bg_color, (0, pos_y), (game_window.get_width(), pos_y), 1, )
        pygame.draw.line(game_window, bg_color, (pos_x, 0), (pos_x, game_window.get_height()), 1, )


def place_mark(click_index, data, player_id, ):
    if data["gameFields"][click_index] == 0:
        data["gameFields"][click_index] = player_id
        return True

    return False


def draw_text(text, game_window, pos, font_size, bg_color=(102, 102, 51), ):
    font_obj = pygame.font.Font('freesansbold.ttf', font_size, )
    text_obj = font_obj.render(text, True, bg_color, )
    text_square = text_obj.get_rect()
    text_square.center = pos
    game_window.blit(text_obj, text_square)
    pygame.display.flip()


def draw_mark(data, player, game_window):
    width_box = game_window.get_width() / 3
    height_box = game_window.get_height() / 3
    font_size = 60
    for i in range(3):
        for j in range(3):
            value = data["gameFields"][(i * 3) + j]
            if player == value:
                draw_text("O", game_window, ((j * width_box + width_box / 2), (i * height_box + height_box / 2)), font_size)
            elif value != 0:
                draw_text("X", game_window, ((j * width_box + width_box / 2), (i * height_box + height_box / 2)), font_size)

    pygame.display.flip()


def print_winner(game_window, win, p_id, ):
    if win == p_id:
        text = u"Wygrałeś"
    elif win == "remis":
        text = u"Remis"
    else:
        text = u"Przegrałeś"

    draw_text(text, game_window, ((game_window.get_width() / 2), (game_window.get_height() / 2)), 36, (204, 0, 0))


def end(sock, game_window=None, error=False, ):
    if error:
        draw_text(u"Utracono połączenie", game_window, (game_window.get_width() / 2, game_window.get_height() / 2), 20, bg_color=(204, 0, 0), )
    sock.close()
    while 1:
        event = pygame.event.wait()
        if event.type == QUIT:
            break
    pygame.quit()
    sys.exit()


def main():
    play = True
    width = 100
    height = 100

    pygame.init()
    game_window = init_window(width, height, )

    s = socket(AF_INET, SOCK_STREAM, )
    s.connect(('', 8888), )
    try:
        data = pickle.loads(s.recv(1024), )
        player_id = data["id"]

        if data.get("wait"):
            draw_text(data["wait"], game_window, (game_window.get_width() / 2, 20), 20, bg_color=(0, 0, 0), )
    except EOFError:
        end(s, game_window, error=True)

    while play:
        action = False

        try:
            data = pickle.loads(s.recv(1024), )
            draw_mark(data, player_id, game_window, )
            pygame.event.clear(MOUSEBUTTONDOWN)

            if data['win']:
                print_winner(game_window, data["win"], player_id, )
                break
        except EOFError:
            end(s, game_window, error=True)

        while not action:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                if (pygame.event.wait().type == MOUSEBUTTONUP) & (event.button == 1):
                    mouse_x, mouse_y = event.pos
                    click_index = ((mouse_y / height) * 3) + (mouse_x / width)
                    if place_mark(click_index, data, player_id):
                        draw_mark(data, player_id, game_window, )
                        action = True
            if event.type == QUIT:
                play = False
                break

        s.send(pickle.dumps(data), )
    end(s)


if __name__ == "__main__":
    main()
