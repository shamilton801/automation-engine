import random
from typing import List, Tuple
from cyberchase import Seeker

class Seeker(Seeker):

    def __init__(self):
        pass


    def get_action_from_state(self,board_states: List[List[int]],
                              visible_squares: List[Tuple[int, int]],
                              valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        return random.choice(valid_moves)
