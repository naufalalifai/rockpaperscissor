import socket
import threading
import tkinter as tk
from tkinter import messagebox

from protocol import encode_message, decode_message

HOST = "127.0.0.1"
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class RPSClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Rock Paper Scissors")

        self.username = tk.StringVar()
        self.status = tk.StringVar(value="Enter username and connect")

        self.create_widgets()
        self.disable_game_buttons()

    def create_widgets(self):
        tk.Label(self.root, text="Username").pack()
        tk.Entry(self.root, textvariable=self.username).pack()

        tk.Button(self.root, text="Connect", command=self.connect).pack(pady=5)

        tk.Label(self.root, textvariable=self.status).pack(pady=10)

        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack()

        self.rock_btn = tk.Button(self.btn_frame, text="Rock", command=lambda: self.send_move("R"))
        self.paper_btn = tk.Button(self.btn_frame, text="Paper", command=lambda: self.send_move("P"))
        self.scissors_btn = tk.Button(self.btn_frame, text="Scissors", command=lambda: self.send_move("S"))

        self.rock_btn.grid(row=0, column=0, padx=5)
        self.paper_btn.grid(row=0, column=1, padx=5)
        self.scissors_btn.grid(row=0, column=2, padx=5)

    def connect(self):
        if not self.username.get():
            messagebox.showerror("Error", "Username required")
            return

        try:
            sock.connect((HOST, PORT))
            sock.sendall(encode_message("JOIN", self.username.get()))
            threading.Thread(target=self.listen_server, daemon=True).start()
            self.status.set("Connected. Waiting for opponent...")
        except Exception as e:
            messagebox.showerror("Connection error", str(e))

    def listen_server(self):
        try:
            while True:
                data = sock.recv(1024)
                if not data:
                    break

                msg_type, payload = decode_message(data)
                self.handle_message(msg_type, payload)
        except Exception as e:
            print("Disconnected:", e)

    def handle_message(self, msg_type, payload):
        if msg_type == "START":
            self.status.set("Game started! Make your move.")
            self.enable_game_buttons()

        elif msg_type == "INFO":
            self.status.set(payload)

        elif msg_type == "RESULT":
            self.status.set(payload)
            self.enable_game_buttons()

        elif msg_type == "GAMEOVER":
            self.status.set(f"Game over! Winner: {payload}")
            self.disable_game_buttons()
            messagebox.showinfo("Game Over", "Match ended. Please restart client to play again.")

        elif msg_type == "ERROR":
            messagebox.showerror("Error", payload)

    def send_move(self, move):
        try:
            sock.sendall(encode_message("MOVE", move))
            self.status.set(f"Move sent: {move}")
            self.disable_game_buttons()
        except:
            messagebox.showerror("Error", "Failed to send move")

    def disable_game_buttons(self):
        self.rock_btn.config(state="disabled")
        self.paper_btn.config(state="disabled")
        self.scissors_btn.config(state="disabled")

    def enable_game_buttons(self):
        self.rock_btn.config(state="normal")
        self.paper_btn.config(state="normal")
        self.scissors_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = RPSClient(root)
    root.mainloop()
