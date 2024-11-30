import copy
import numpy as np

# from TablutProject.Domain.Action import Action
from typing import List, Tuple

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


class State:
    def __init__(self, turn: str):
        self.turn = turn
        self.board = np.zeros((9, 9), dtype=np.int8)
        self.board[4, 4] = KING

        self.board[2, 4] = WHITE
        self.board[3, 4] = WHITE
        self.board[5, 4] = WHITE
        self.board[6, 4] = WHITE
        self.board[4, 2] = WHITE
        self.board[4, 3] = WHITE
        self.board[4, 5] = WHITE
        self.board[4, 6] = WHITE

        self.board[0, 3] = BLACK
        self.board[0, 4] = BLACK
        self.board[0, 5] = BLACK
        self.board[1, 4] = BLACK
        self.board[8, 3] = BLACK
        self.board[8, 4] = BLACK
        self.board[8, 5] = BLACK
        self.board[7, 4] = BLACK
        self.board[3, 0] = BLACK
        self.board[4, 0] = BLACK
        self.board[5, 0] = BLACK
        self.board[4, 1] = BLACK
        self.board[3, 8] = BLACK
        self.board[4, 8] = BLACK
        self.board[5, 8] = BLACK
        self.board[4, 7] = BLACK

    def remove_pawn(self, row, column):
        self.board[row, column] = EMPTY

    def set_board(self, board):
        # Conversione da board server a board numpy
        d = {
            "WHITE": WHITE,
            "EMPTY": EMPTY,
            "BLACK": BLACK,
            "KING": KING,
            "THRONE": EMPTY,
        }
        self.board = np.zeros((9, 9))
        for i in range(9):
            for j in range(9):
                self.board[i, j] = d[board[i][j]]

    def set_turn(self, turn):
        self.turn = turn

    def get_moves(self, board, i, j) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Ritorna tutte le possibili mosse della pedina in posizione i,j
        """
        # Verifica che ci sia una pedina nella posizione
        if board[i, j] == EMPTY:
            return []

        # Matrice booleana delle caselle vuote
        is_empty = np.logical_and(board == EMPTY, ~black_camp)

        is_empty[4, 4] = False

        # Solo il re puo' passare dal centro
        """ if board[i, j] == KING:
            is_empty[4, 4] = True
        else:
            is_empty[4, 4] = False """

        # Righe e colonne pertinenti
        row = is_empty[i, :]
        col = is_empty[:, j]

        # Trova i limiti sulle righe
        left_limit = max(np.where(~row[:j])[0], default=-1) + 1
        right_limit = min(np.where(~row[j + 1 :])[0], default=row.size - j - 1) + j

        # Trova i limiti sulle colonne
        top_limit = max(np.where(~col[:i])[0], default=-1) + 1
        bottom_limit = min(np.where(~col[i + 1 :])[0], default=col.size - i - 1) + i

        # Genera le posizioni valide
        moves = []

        # Aggiungi mosse nella riga
        moves.extend(
            ((i, j), (i, x)) for x in range(left_limit, right_limit + 1) if x != j
        )
        # Aggiungi mosse nella colonna
        moves.extend(
            ((i, j), (y, j)) for y in range(top_limit, bottom_limit + 1) if y != i
        )

        return moves

    def ammissible_actions(
        self, color: str
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        ammissible_actions = []
        for i in range(9):
            for j in range(9):
                if (
                    (self.board[i, j] == BLACK and color == "BLACK")
                    or (self.board[i, j] == WHITE and color == "WHITE")
                    or (self.board[i, j] == KING and color == "WHITE")
                ):
                    ammissible_actions += self.get_moves(self.board, i, j)
        return ammissible_actions

    def __eq__(self, other):
        if not isinstance(other, State):
            return False
        if self.board != other.board:
            return False
        if self.turn != other.turn:
            return False
        return True

    def __hash__(self):
        return hash((tuple(tuple(row) for row in self.board), self.turn))

    def is_terminal(self) -> Tuple[bool, str]:
        # Check if white wins (king in the corner)
        king_position = np.where(self.board == KING)
        if king_winning_positions[king_position[0], king_position[1]]:
            return True, "WHITE"

        # Check if black wins (king captured)
        # Check the 4 adjacent cells
        king_row = king_position[0]
        king_col = king_position[1]
        if (
            (
                self.board[king_row - 1, king_col] == BLACK
                or (king_row - 1 == 4 and king_col == 4)
            )
            and (
                self.board[king_row + 1, king_col] == BLACK
                or (king_row + 1 == 4 and king_col == 4)
            )
            and (
                self.board[king_row, king_col - 1] == BLACK
                or (king_row == 4 and king_col - 1 == 4)
            )
            and (
                self.board[king_row, king_col + 1] == BLACK
                or (king_row == 4 and king_col + 1 == 4)
            )
        ):
            return True, "BLACK"

        return False, ""

    def move(self, action: Tuple[Tuple[int, int], Tuple[int, int]]):
        start, end = action
        new_board = self.board.copy()
        new_board[end[0], end[1]] = new_board[start[0], start[1]]
        new_board[start[0], start[1]] = EMPTY

        # Check if some pawns are captured
        opponent_color = BLACK if self.turn == "WHITE" else WHITE
        self_color = WHITE if self.turn == "WHITE" else BLACK
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            middle_row = end[0] + dr
            middle_col = end[1] + dc
            ending_row = end[0] + 2 * dr
            ending_col = end[1] + 2 * dc

            if 0 <= middle_row < 9 and 0 <= middle_col < 9:
                if new_board[middle_row, middle_col] == opponent_color:
                    if 0 <= ending_row < 9 and 0 <= ending_col < 9:
                        if (
                            (new_board[ending_row, ending_col] == self_color)
                            or (black_camp[ending_row, ending_col])
                            or (ending_row == 4 and ending_col == 4)  # Throne
                        ):
                            new_board[middle_row, middle_col] = EMPTY

        new_state = copy.deepcopy(self)
        new_state.board = new_board
        new_state.turn = "WHITE" if self.turn == "BLACK" else "BLACK"
        return new_state
