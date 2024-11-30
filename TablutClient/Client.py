import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
# from TablutProject.State import State
import time
import random
import argparse

# from TablutProject.Utils.Utils import StreamUtils
import socket
import json

# from TablutProject.Utils.Utils import StreamUtils

# from TablutProject.State import State
import logging
import struct
from Search import _min_max
from State import State

logging.basicConfig(level=logging.INFO)

WHITE_PORT = 5800
BLACK_PORT = 5801


def recvall(sock, n):
    # Funzione ausiliaria per ricevere n byte o restituire None se viene raggiunta la fine del file (EOF)
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def fromIndexToLetters(position):
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    return letters[position[1]] + str(position[0] + 1)


class Client:
    def __init__(self, player, name, timeout=60, ip_address="localhost"):
        """
        Initializes a new player, setting up sockets and configuration.

        :param player: Role of the player ("black" or "white")
        :param name: Name of the player
        :param timeout: Timeout in seconds (default is 60)
        :param ip_address: IP address of the server (default is "localhost")
        """
        self.name = name
        self.timeout = timeout
        self.server_ip = ip_address

        if player.lower() == "white":
            self.player = "WHITE"
            self.port = WHITE_PORT
        elif player.lower() == "black":
            self.player = "BLACK"
            self.port = BLACK_PORT
        else:
            raise ValueError("Player role must be 'black' or 'white'")

        self.current_state: State = State(self.player)
        # Setting up the socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"Connessione al server {self.server_ip}:{self.port}")
        self.socket.connect((self.server_ip, self.port))
        logging.info("Connessione effettuata")

    def sendAction(self, action):
        """
        Sends an action to the server.

        :param action: The action to send (dictionary or object serializable to JSON)
        """
        mossa = {
            "from": fromIndexToLetters(action[0]),
            "to": fromIndexToLetters(action[1]),
            "turn": "W" if self.player == "WHITE" else "B",
        }

        to_send = json.dumps(mossa)
        logging.info(f"Sending action to server {to_send}")
        self.sendToServer(to_send)

    def declare_name(self):
        """
        Sends the player's name to the server.
        """
        logging.info(f"Invio nome {self.name}")
        self.sendToServer(self.name)
        logging.info("Invio nome effettuato")

    def sendToServer(self, data):
        # Invia la lunghezza dei dati di stato corrente dal server e poi i dati stessi
        data_bytes = data.encode()
        self.socket.send(struct.pack(">i", len(data_bytes)))
        self.socket.send(data_bytes)

    def receiveStateFromServer(self):
        # Ricevi la lunghezza dei dati di stato corrente dal server e poi i dati stessi
        len_bytes = struct.unpack(">i", recvall(self.socket, 4))[0]
        current_state_server_bytes = self.socket.recv(len_bytes)

        # Decodifica i dati di stato in formato JSON
        json_current_state_server = json.loads(current_state_server_bytes)
        board = json_current_state_server["board"]
        turn = json_current_state_server["turn"].lower()

        if turn == "draw":
            logging.info("Draw")
            exit()
        elif (turn == "whitewin" and self.player == "WHITE") or (
            turn == "blackwin" and self.player == "BLACK"
        ):
            logging.info("SIUM")
            exit()
        elif (turn == "whitewin" and self.player == "BLACK") or (
            turn == "blackwin" and self.player == "WHITE"
        ):
            logging.info("SAD FACE")
            exit()

        turn = turn.upper()

        self.current_state.set_board(board)
        self.current_state.set_turn(turn)

        return turn, board

    def close(self):
        """
        Closes the connection to the server.
        """
        logging.info("Closing connection to server")
        self.socket.close()

    def play(self):
        while True:
            self.receiveStateFromServer()

            logging.info(f"Current state: {self.current_state}")
            logging.info(f"Turn: {self.current_state.turn}")

            if self.player != self.current_state.turn:
                logging.info("Waiting for opponent move ... ")
                continue

            depth = 1
            # last_res = -1000
            last_action = None
            logging.info("Starting search")
            while True:
                res, action, explored_nodes = _min_max(
                    self.current_state,
                    self.player,
                    depth,
                    -float("inf"),
                    +float("inf"),
                    time.time() + self.timeout,
                )
                logging.info(
                    f"Depth: {depth}, Res: {res}, Best action: {action}, Explored nodes: {explored_nodes}"
                )
                if res is None:
                    depth -= 1
                    break
                # last_res = res
                last_action = action
                depth += 1

            logging.info(f"Best action: {last_action}")
            self.sendAction(last_action)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client for Tablut")
    parser.add_argument(
        "-p",
        "--player",
        help="Player role (white or black)",
        required=True,
        # choices=["white", "black"],
        default="white",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        help="Timeout in seconds",
        required=True,
        default=60,
    )
    parser.add_argument(
        "-i",
        "--ip",
        help="IP address of the server",
        required=True,
        default="127.0.0.1",
    )

    args = parser.parse_args()

    client = Client(args.player, "Tabluxemburg", int(args.timeout), args.ip)
    client.declare_name()

    client.play()
