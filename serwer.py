# coding=utf-8
from socket import *
import errno
import pickle


def check_win(game_data, client1, client2, client_id1, client_id2):

    def field(xx, yy, game_fields, ):
        return game_fields[xx + yy * 3]

    def win(game_fields, id1, id2):
        play1 = [id1] * 3
        play2 = [id2] * 3
        seq = range(3)

        for x in seq:
            row = [field(x, y, game_fields, ) for y in seq]
            col = [field(y, x, game_fields, ) for y in seq]
            if row == play1 or col == play1:
                return id1

            elif row == play2 or col == play2:
                return id2

        diagonal1 = [field(i, i, game_fields, ) for i in seq]
        diagonal2 = [field(i, abs(i-2), game_fields, ) for i in seq]
        if diagonal1 == play1 or diagonal2 == play1:
            return id1
        if diagonal1 == play2 or diagonal2 == play1:
            return id2

        if not (0 in game_fields):
            return "remis"

    winn = win(game_data["gameFields"], client_id1, client_id2)
    if winn:
        game_data["win"] = winn
        client1.send(pickle.dumps(game_data))
        client2.send(pickle.dumps(game_data))
        return True


def end(client, client2, s, error=False):
    if error:
        print("błąd")
    client.close()
    client2.close()
    s.close()
    main()


def main():
    s = socket(AF_INET, SOCK_STREAM, )
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(('', 8888), )
    s.listen(5)
    game_data = dict(gameFields=[
        0, 0, 0,
        0, 0, 0,
        0, 0, 0,
    ], winning=0, win=False,)

    try:
        client1, client_id1 = s.accept()
        client_id1 = client_id1[1]
        client1.send(pickle.dumps({"id": client_id1, "wait": "Poczekaj na drugiego gracza"}))

        client2, client_id2 = s.accept()
        client_id2 = client_id2[1]
        client2.send(pickle.dumps({"id": client_id2}))
    except EOFError:
        end(client1, client2, s, error=True)

    while not game_data["win"]:

        try:
            client1.send(pickle.dumps(game_data))
            game_data = pickle.loads(client1.recv(1024))
        except (EOFError, KeyboardInterrupt, error, ):
            end(client1, client2, s, error=True)

        if check_win(game_data, client1, client2, client_id1, client_id2):
            break
        print("ta")
        try:
            client2.send(pickle.dumps(game_data))
            game_data = pickle.loads(client2.recv(1024))
        except (EOFError, KeyboardInterrupt, error, ):
            end(client1, client2, s, error=True)

        if check_win(game_data, client1, client2, client_id1, client_id2):
            break

    end(client1, client2, s, )

if __name__ == "__main__":
    main()
