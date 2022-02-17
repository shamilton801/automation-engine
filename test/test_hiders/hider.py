import random
from typing import List, Tuple
from cyberchase import Hider

class Hider(Hider):
    def __init__(self):
        pass

    def get_action_from_state(self, board_states: List[List[int]],
                              visible_squares: List[Tuple[int, int]],
                              valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        move = random.choice(valid_moves)
        return move
