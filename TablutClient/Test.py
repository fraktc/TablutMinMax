from State import State
from Search import _min_max
import numpy as np
import time

EMPTY = 0
WHITE = 1
BLACK = 2
KING = 3

initial_state = State("WHITE")
initial_state.board = np.array(
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


res, best_action, explored_nodes = _min_max(
    initial_state, "WHITE", 4, -np.inf, +np.inf, time.time() + 60
)

print(len(initial_state.ammissible_actions("WHITE")))
print(res, best_action, explored_nodes)
