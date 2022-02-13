# Sample submission seeker python file
from typing import List, Tuple
import random
from collections import deque
from board import Board


class Seeker:
    """
    The scotland yard algorithm is based on prioritizing the least recently seen square. 

    A dictionary is used to keep track of visited history. It maps coordinates -> turn nums

    Each turn, scotland yard checks whether the hider is in sight. 

    The hider is visible: scotland yard uses pathfinding to move in the direction of the hider. 
                          coordinate turn nums are updated

    The hider is invisible: The scotland yard checks which of the available squares is has
                            the lowest (oldest) turn num (prioritizing between equal options randomly).

                            Herin lies a potential optimization: prioritize choosing squares that are closer
                            to new squares (when prioritizing between equlivalent options)

    Note for different approach: this algorithm simply focuses on covering new ground. There might be optimal 
                                 squares to optimize line-of-sight instead. (The seeker wins the sooner it sees the hider)  

    """

    SEARCHING = 1
    CHASING = 2

    def __init__(self):
        self.coord_to_turn = {}

        self.cur_loc = None
        self.turn_num = 0

        self.state = self.SEARCHING
        self.prev_state = self.CHASING

    def get_action_from_state(self, board_state: List[List[int]],
                              visible_squares: List[Tuple[int, int]],
                              valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:

        self.prev_state = self.state

        self.board_state = board_state
        self.visible_squares = visible_squares
        self.valid_moves = valid_moves
        self.turn_num += 1

        if self.cur_loc == None:
            self._set_cur_loc()

        self.hider_loc = self._get_hider_loc()
        if self.hider_loc is None:
            self.state = self.SEARCHING
            choice = self._move_to_lrs_square()
        else:
            self.state = self.CHASING
            choice = self._move_towards_hider()

        self.cur_loc = choice
        return choice

    def _set_cur_loc(self):
        for i, row in enumerate(self.board_state):
            for j, val in enumerate(row):
                if val == 1:
                    self.cur_loc = (i, j)
                    return

    def _get_hider_loc(self) -> Tuple:
        # Returns None if hider is not in sight, otherwise returns hider's coordinate
        for s in self.visible_squares:
            if self.board_state[s[0], s[1]] == Board.PLAYER_2:
                return s

        return None


    def _move_to_lrs_square(self):
        # lrs = least recently seen square. see class notes
        best = 999
        best_moves = [self.cur_loc]
        for m in self.valid_moves:
            if m not in self.coord_to_turn:
                self.coord_to_turn[m] = 0

            if self.coord_to_turn[m] < best:
                best = self.coord_to_turn[m]
                best_moves = [m]
            elif self.coord_to_turn[m] == best:
                best_moves.append(m)

        # Choosing random move from equally good options. 
        # TODO: Good optimization potential here!
        final_m = random.choice(best_moves)

        self._update_mem(final_m)
        return final_m

    def _update_mem(self, final_m):
        path = self._get_shortest_path(self.cur_loc, final_m)
        for s in path:           
            self.coord_to_turn[s] = self.turn_num

        self.coord_to_turn[self.cur_loc] = self.turn_num

    def _get_shortest_path(self, start, stop):
        # Runs a simple BFS search till the stop position is reached
        # A-star search probably won't really give any benefits given how small 
        # and restrictive the maps are

        parent_map = {} # map of loc to parent loc. start loc has "None" parent
        q = deque([(start, None)])


        while len(q) > 0:
            loc, par_loc = q.pop()

            if loc in parent_map:
                continue
            parent_map[loc] = par_loc

            if loc == stop:
                break

            for new_loc in self._get_valid_neighbors(loc):
                q.appendleft((new_loc, loc))

        res = []
        cur_loc = stop
        while cur_loc != start:
            res.append(cur_loc)
            cur_loc = parent_map[cur_loc]
        res.reverse()

        return res

    def _get_valid_neighbors(self, loc):
        up = (loc[0]-1, loc[1])
        down = (loc[0]+1, loc[1])
        left = (loc[0], loc[1]-1)
        right = (loc[0], loc[1]+1)

        potential = [up, down, left, right]
        for new_loc in potential:
            if (new_loc[0] < 0 or 
                new_loc[1] < 0 or 
                new_loc[0] >= len(self.board_state) or 
                new_loc[1] >= len(self.board_state[0]) or 
                self.board_state[new_loc[0], new_loc[1]] == 3):
                potential.remove(new_loc)

        return potential

    def _move_towards_hider(self):
        path = self._get_shortest_path(self.cur_loc, self.hider_loc)
        best = path[0]
        for p in path:
            if p in self.valid_moves:
                best = p
        return best