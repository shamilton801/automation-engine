from board import Board
import numpy as np
import time
from hider import Hider
from seeker import Seeker
from typing import List, Tuple

class SeekerException(Exception):
    pass

class HiderException(Exception):
    pass

class Game:
    SEEKER = 1
    HIDER = 2

    def __init__(self, hider_bot: Hider, seeker_bot: Seeker, seed: int, render=True):
        self.hider_bot = hider_bot
        self.seeker_bot = seeker_bot

        self.board = Board(30, 30, seed, "perlin", render=render)

        self.turns_complete = 0
        self.max_turns = 250

    def game_loop(self):
        turn_value = self.turn()
        while turn_value == 0:
            if self.board.render:
                self.board.draw()
                # time.sleep(0.2)
            turn_value = self.turn()
        if turn_value == 1:
            print("Seeker wins!")
            return self.SEEKER, self.turns_complete
        else:
            print("Hider wins!")
            return self.HIDER, self.turns_complete

    def get_player_states(self, player: int) -> Tuple[List[List[int]], List[Tuple[int, int]], List[Tuple[int, int]]]:
        player_position = self.board.player_1_pos if player == self.SEEKER else self.board.player_2_pos
        other_player_position = self.board.player_2_pos if player == self.SEEKER else self.board.player_1_pos
        player_movement = 5 if player == self.SEEKER else 4
        visible_squares = self.board.get_visible_squares(player_position)
        curr_board_states = np.copy(self.board.board_states)
        if other_player_position not in visible_squares:
            curr_board_states[other_player_position[0], other_player_position[1]] = self.board.AVAILABLE
        # Probably also give possible moves for that player
        valid_moves = self.board.walk_board(player_position, player_movement)
        return curr_board_states, visible_squares, valid_moves

    # Gives each player a turn, checks if board is in win state after each turn
    # hider_action should be a valid move from the set and tells where to move the bot this turn
    def turn(self) -> int:
        board_states, visible_squares, valid_moves = self.get_player_states(self.HIDER)
        # Make a copy to pass to the player so they can't modify
        valid_moves_copy = list(valid_moves)
        
        try:
            hider_action = self.hider_bot.get_action_from_state(board_states, visible_squares, valid_moves_copy)
        except Exception as e:
            raise HiderException(e)

        hider_pos = self.board.player_2_pos
        if hider_action not in valid_moves:
            print("Hider has entered an invalid move, not moving the hider!")
            hider_action = hider_pos
        else:
            self.board.board_states[hider_pos[0], hider_pos[1]] = self.board.AVAILABLE
            self.board.board_states[hider_action[0], hider_action[1]] = self.board.PLAYER_2
            self.board.player_2_pos = hider_action
        win = self.check_win()
        if win:
            return win

        # Seekers turn
        board_states, visible_squares, valid_moves = self.get_player_states(self.SEEKER)
        # Make a copy to pass to the player so they can't modify
        valid_moves_copy = list(valid_moves)
        
        try:
            seeker_action = self.seeker_bot.get_action_from_state(board_states, visible_squares, valid_moves_copy)
        except Exception as e:
            raise SeekerException(e)
        
        seeker_pos = self.board.player_1_pos
        if seeker_action not in valid_moves:
            print("Seeker has entered an invalid move, not moving the seeker!")
            seeker_action = seeker_pos
        else:
            self.board.board_states[seeker_pos[0], seeker_pos[1]] = self.board.AVAILABLE
            self.board.board_states[seeker_action[0], seeker_action[1]] = self.board.PLAYER_1
            self.board.player_1_pos = seeker_action
        win = self.check_win()
        if win:
            return win

        self.turns_complete += 1
        return 0

    # Checks if seeker is adjacent to hider or if the turn limit has been reached
    def check_win(self) -> int:
        if self.turns_complete == self.max_turns:
            return self.HIDER
        return self.SEEKER if abs(self.board.player_1_pos[0] - self.board.player_2_pos[0]) + abs(self.board.player_1_pos[1] - self.board.player_2_pos[1]) == 1 else 0