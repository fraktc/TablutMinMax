from State import State
import numpy as np
import time

EMPTY = 0
WHITE = 1
BLACK = 2
KING = 3


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

king_winning_positions = np.array(
    [
        [1, 1, 1, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 0, 0, 1, 1, 1],
    ],
    dtype=np.bool,
)

# Load the model
import joblib

ML_MODEL = joblib.load("model.pkl")


def _min_max(
    state: State,
    player: str,
    max_depth: int,
    alpha: float,
    beta: float,
    timeout_timestamp: float,
    explored_nodes: int = 0,
):
    explored_nodes += 1
    if state.turn != player:
        raise Exception("state.turn should be equal to player")

    is_terminal, winner = state.is_terminal()
    if is_terminal:
        if winner == "WHITE":
            return 100, None, explored_nodes
        else:
            return -100, None, explored_nodes

    if max_depth == 0:
        return hueristic(state, player), None, explored_nodes

    best_action = None

    if player == "WHITE" and state.turn == "WHITE":
        # Maximize
        value = -np.inf
        for action in state.ammissible_actions(player):
            if time.time() > timeout_timestamp:
                return None, None, None
            new_state = state.move(action)
            new_value, _, explored_nodes = _min_max(
                new_state,
                "BLACK",
                max_depth - 1,
                alpha,
                beta,
                timeout_timestamp,
                explored_nodes,
            )

            if new_value is None:
                return None, None, None  # Timeout
            if new_value > value:
                value = new_value
                best_action = action
            alpha = max(alpha, value)
            if beta <= alpha:
                break

    else:
        # Minimize
        value = np.inf
        for action in state.ammissible_actions(player):
            if time.time() > timeout_timestamp:
                return None, None, None
            new_state = state.move(action)
            new_value, _, explored_nodes = _min_max(
                new_state,
                "WHITE",
                max_depth - 1,
                alpha,
                beta,
                timeout_timestamp,
                explored_nodes,
            )
            if new_value is None:
                return None, None, None  # Timeout
            if new_value < value:
                value = new_value
                best_action = action
            beta = min(beta, value)
            if beta <= alpha:
                break

    return value, best_action, explored_nodes


def hueristic(state: State, player: str) -> float:
    h1 = num_pieces_ratio(state.board, player)
    h2 = king_distance(state.board, player)
    h3 = average_piece_safety(state.board, player)
    h4 = king_safety(state.board, player)

    return ML_MODEL.predict([[h1, h2, h3, h4]])[0]


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
