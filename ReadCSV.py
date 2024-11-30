import csv
import os

import numpy as np
from tqdm import tqdm


EMPTY = 0
WHITE = 1
BLACK = 2
KING = 3
file = "results.csv"

black_camp = np.array(
    [
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 0, 0, 0, 0, 0, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
    ],
    dtype=np.bool,
)

initial_state = np.array(
    [
        [EMPTY, EMPTY, EMPTY, BLACK, BLACK, BLACK, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, EMPTY, BLACK, EMPTY, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, EMPTY, BLACK, BLACK, EMPTY, EMPTY, EMPTY],
        [BLACK, EMPTY, EMPTY, BLACK, KING, EMPTY, EMPTY, WHITE, BLACK],
        [BLACK, BLACK, WHITE, WHITE, EMPTY, WHITE, WHITE, BLACK, BLACK],
        [BLACK, EMPTY, EMPTY, EMPTY, WHITE, EMPTY, EMPTY, EMPTY, BLACK],
        [EMPTY, EMPTY, EMPTY, EMPTY, WHITE, EMPTY, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, EMPTY, BLACK, EMPTY, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, BLACK, BLACK, BLACK, EMPTY, EMPTY, EMPTY],
    ]
)


def num_pieces_ratio(board, turn):
    white = np.sum(board == WHITE) / 9
    black = np.sum(board == BLACK) / 16
    if turn == "WHITE":
        return 2 * np.tanh(white / black) - 1
    else:
        return 2 * np.tanh(black / white) - 1


def king_distance(board, turn):
    king = np.argwhere(board == KING)[0]
    distance = np.linalg.norm(king - np.array([4, 4])) / np.sqrt(32)
    if turn == "WHITE":
        return 2 * np.tanh(distance) - 1
    else:
        return 2 * np.tanh(1 - distance) - 1


def average_piece_safety(board, turn):
    if turn == "WHITE":
        pawns = np.argwhere(board == WHITE)
        total_safety = 0
        for pawn in pawns:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            safe = True
            for d in directions:
                if 0 <= pawn[0] + d[0] < 9 and 0 <= pawn[1] + d[1] < 9:
                    if (
                        (board[pawn[0] + d[0], pawn[1] + d[1]] == BLACK)
                        or (black_camp[pawn[0] + d[0], pawn[1] + d[1]])
                        or (pawn[0] + d[0] == 4 and pawn[1] + d[1] == 4)
                    ):
                        total_safety -= 0.5
                        safe = False
                        break
            if safe:
                total_safety += 1
        return total_safety / len(pawns)
    else:
        pawns = np.argwhere(board == BLACK)
        total_safety = 0
        for pawn in pawns:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            safe = True
            for d in directions:
                if 0 <= pawn[0] + d[0] < 9 and 0 <= pawn[1] + d[1] < 9:
                    if (
                        (board[pawn[0] + d[0], pawn[1] + d[1]] == WHITE)
                        or (black_camp[pawn[0] + d[0], pawn[1] + d[1]])
                        or (pawn[0] + d[0] == 4 and pawn[1] + d[1] == 4)
                    ):
                        total_safety -= 0.5
                        safe = False
                        break
            if safe:
                total_safety += 1
        return total_safety / len(pawns)


def king_safety(board, turn):
    king = np.argwhere(board == KING)[0]
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if king[0] == 4 and king[1] == 4:
        total_safety = 1
        for d in directions:
            if 0 <= king[0] + d[0] < 9 and 0 <= king[1] + d[1] < 9:
                if board[king[0] + d[0], king[1] + d[1]] == BLACK:
                    total_safety -= 0.5
    elif (
        (king[0] == 3 and king[1] == 4)
        or (king[0] == 5 and king[1] == 4)
        or (king[0] == 4 and king[1] == 3)
        or (king[0] == 4 and king[1] == 5)
    ):
        total_safety = 1
        for d in directions:
            if 0 <= king[0] + d[0] < 9 and 0 <= king[1] + d[1] < 9:
                if board[king[0] + d[0], king[1] + d[1]] == BLACK:
                    total_safety -= 0.75
    else:
        total_safety = 1
        for d in directions:
            if 0 <= king[0] + d[0] < 9 and 0 <= king[1] + d[1] < 9:
                if board[king[0] + d[0], king[1] + d[1]] == BLACK:
                    total_safety -= 1
    if turn == "WHITE":
        return total_safety
    else:
        return -total_safety


headers = [f"cell_{i}" for i in range(81)] + [
    "turn",
    "winner",
    "turn_number",
    "total_turns",
]

new_headers = [f"h_{i}" for i in range(4)] + ["y"]

# Read the csv file
with open(file, "r") as f:
    with open("output.csv", "w", newline="") as f_out:
        writer = csv.writer(f_out, delimiter=",")
        writer.writerow(new_headers)

        reader = csv.reader(f)
        for i, row in tqdm(enumerate(reader)):
            if i == 0:
                # print(row)

                assert row == headers
            else:
                data = row
                cells = np.array(data[:81], dtype=int).reshape(9, 9)
                if np.array_equal(cells, initial_state):
                    continue
                turn = int(data[81])
                winner = int(data[82])
                turn_number = int(data[83])
                total_turns = int(data[84])

                h1 = num_pieces_ratio(cells, turn)
                h2 = king_distance(cells, turn)
                h3 = average_piece_safety(cells, turn)
                h4 = king_safety(cells, turn)

                if winner == 999:
                    y = 0
                else:
                    if winner == turn:
                        y = 1 * (turn_number / total_turns)
                    else:
                        y = -1 * (turn_number / total_turns)

                new_row = [h1, h2, h3, h4, y]
                # print(new_row)
                writer.writerow(new_row)
