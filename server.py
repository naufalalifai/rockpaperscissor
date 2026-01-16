from dotenv import load_dotenv
load_dotenv()

import socket
import threading
import time

from protocol import encode_message, decode_message
from email_util import send_winner_email

HOST = "0.0.0.0"
PORT = 5000
TIMEOUT = 10  # seconds

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(2)

print("Server started. Waiting for players...")

players = {}
lock = threading.Lock()
round_number = 1
game_active = True


def determine_winner(move1, move2):
    if move1 == move2:
        return 0
    wins = {
        ("R", "S"),
        ("S", "P"),
        ("P", "R")
    }
    return 1 if (move1, move2) in wins else 2


def broadcast(msg_type, payload=""):
    for conn in players:
        try:
            conn.sendall(encode_message(msg_type, payload))
        except:
            pass


def handle_client(conn):
    global round_number, game_active

    conn.settimeout(TIMEOUT)

    try:
        data = conn.recv(1024)
        msg_type, payload = decode_message(data)

        if msg_type != "JOIN":
            conn.sendall(encode_message("ERROR", "Expected JOIN"))
            conn.close()
            return

        with lock:
            players[conn]["name"] = payload

        conn.sendall(encode_message("INFO", "Waiting for opponent..."))

        while len(players) < 2:
            time.sleep(0.5)

        conn.sendall(encode_message("START", "Game started"))

        while game_active:
            try:
                data = conn.recv(1024)
                msg_type, payload = decode_message(data)

                if msg_type == "MOVE":
                    with lock:
                        players[conn]["move"] = payload

            except socket.timeout:
                with lock:
                    players[conn]["move"] = "TIMEOUT"

    except Exception as e:
        print("Client error:", e)
    finally:
        conn.close()


def game_loop():
    global round_number, game_active

    while game_active:
        time.sleep(1)

        with lock:
            if len(players) < 2:
                continue

            moves = list(players.values())
            if any(p["move"] is None for p in moves):
                continue

            p1, p2 = list(players.items())
            move1 = p1[1]["move"]
            move2 = p2[1]["move"]

            if "TIMEOUT" in (move1, move2):
                if move1 == "TIMEOUT" and move2 != "TIMEOUT":
                    p2[1]["score"] += 1
                elif move2 == "TIMEOUT" and move1 != "TIMEOUT":
                    p1[1]["score"] += 1
                broadcast("INFO", "Timeout occurred")
            else:
                result = determine_winner(move1, move2)
                if result == 1:
                    p1[1]["score"] += 1
                elif result == 2:
                    p2[1]["score"] += 1

            broadcast("RESULT", f"Round {round_number} complete")
            round_number += 1

            for p in players.values():
                p["move"] = None

            if p1[1]["score"] == 2 or p2[1]["score"] == 2:
                winner = p1 if p1[1]["score"] > p2[1]["score"] else p2
                broadcast("GAMEOVER", winner[1]["name"])

                try:
                    send_winner_email(winner[1]["name"])
                except Exception as e:
                    print("Email error:", e)

                game_active = False


# Accept players
while len(players) < 2:
    conn, addr = server_socket.accept()
    print("Connected:", addr)
    players[conn] = {"name": "", "move": None, "score": 0}
    threading.Thread(target=handle_client, args=(conn,), daemon=True).start()

# Start game logic
game_loop()
