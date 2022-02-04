import numpy as np
from perlin_noise.perlin_noise import PerlinNoise
import pygame
from typing import Tuple, List
from fractions import Fraction


class Board:
    AVAILABLE = 0
    PLAYER_1 = 1
    PLAYER_2 = 2
    WALL = 3
    PLAYER_1_VISION = 4
    PLAYER_2_VISION = 5

    PLAYER_1_START = (2, 2)
    PLAYER_2_START = (27, 27)

    def __init__(self, height: int, width: int, seed: int, generation_method: str, render: bool = False, seeker_loc=PLAYER_1_START, hider_loc=PLAYER_2_START):
        self.render = render
        self.height = height
        self.width = width
        self.seed = seed

        self.player_1_pos = seeker_loc
        self.player_2_pos = hider_loc

        self._generate_new_board(seed, generation_method, render)
       
    def _generate_new_board(self, seed, generation_method, render):
        if render:
            pygame.init()
            self.square_render_size = 20
            self.screen = pygame.display.set_mode([self.height * self.square_render_size, self.width * self.square_render_size])
            self.colors = {self.AVAILABLE: (255, 255, 255), self.PLAYER_1: (255, 0, 0), self.PLAYER_2: (0, 0, 255),
                           self.WALL: (0, 0, 0), self.PLAYER_1_VISION: (255, 105, 180),
                           self.PLAYER_2_VISION: (0, 255, 255)}

        self.board_states = np.zeros((self.width, self.height), dtype=np.int8)

        for i in range(self.height):
            self.board_states[0, i] = self.WALL
            self.board_states[self.width - 1, i] = self.WALL
        for i in range(self.width):
            self.board_states[i, 0] = self.WALL
            self.board_states[i, self.height - 1] = self.WALL

        if generation_method == "perlin":
            noise = PerlinNoise(octaves=12, seed=seed)
            for i in range(1, self.width - 1):
                for j in range(1, self.height - 1):
                    # print(noise([i / self.width, j / self.height]))
                    if noise([i / self.width, j / self.height]) > 0.1:
                        self.board_states[i, j] = self.WALL

        # Validation Check
        self.valid = self.board_states[self.player_1_pos] != self.WALL
        self.valid &= self.board_states[self.player_2_pos] != self.WALL

        self.board_states[self.player_1_pos] = self.PLAYER_1
        self.board_states[self.player_2_pos] = self.PLAYER_2

        walked = self.walk_board(self.player_1_pos, 100)

        # There exists some path between the two players
        self.valid &= bool(self.player_2_pos in walked)

        # Set any unvisitable squares to be walls for simplicity
        for i in range(1, self.width - 1):
            for j in range(1, self.height - 1):
                if self.board_states[i, j] != self.WALL and (i, j) not in walked:
                    self.board_states[i, j] = self.WALL
                # elif self.board_states[i, j] != self.WALL:
                #     if self.is_visible_integrated(self.player_1_pos, (i, j)) and self.board_states[i, j] != self.PLAYER_1:
                #         self.board_states[i, j] = self.PLAYER_1_VISION

        self.player_1_pos = self.player_1_pos
        self.player_2_pos = self.player_2_pos

        for square in self.get_visible_squares(self.player_1_pos):
            i, j = square
            self.board_states[i, j] = self.PLAYER_1_VISION

        for square in self.get_visible_squares(self.player_2_pos):
            i, j = square
            self.board_states[i, j] = self.PLAYER_2_VISION

        # print(self.board_states)
        if not self.valid:
            print("Not ", end="")
        print("Valid")

    @classmethod
    def from_board_state(board_state: List[List[int]], seeker_loc: Tuple[int, int], hider_loc: Tuple[int, int]):
        return Board(len(board_state), len(board_state[0]), None, None, board_state, seeker_loc, hider_loc)

    def walk_board(self, start_pos: Tuple[int, int], max_depth: int) -> List[Tuple[int, int]]:
        # Perform BFS
        visited = np.zeros(self.board_states.shape)
        visited[start_pos] = 1
        queue = [(start_pos, 1)]
        while len(queue):
            curr, depth = queue.pop(0)
            neighbors = [(curr[0] + 1, curr[1]),
                         (curr[0] - 1, curr[1]),
                         (curr[0], curr[1] - 1),
                         (curr[0], curr[1] + 1)]
            for neighbor in neighbors:
                if not visited[neighbor] and self.board_states[neighbor] != self.WALL and depth < max_depth:
                    visited[neighbor] = 1
                    queue.append((neighbor, depth + 1))
        tuple_of_indices = np.where(visited == 1)
        return [(i, j) for i, j in zip(tuple_of_indices[0], tuple_of_indices[1])]

    def draw(self):
        self.screen.fill((0, 0, 0))
        for i in range(self.board_states.shape[0]):
            for j in range(self.board_states.shape[1]):
                color = self.colors[self.board_states[i, j]]
                pygame.draw.rect(self.screen, color,
                                 pygame.Rect(i * self.square_render_size, j * self.square_render_size,
                                             self.square_render_size, self.square_render_size))
        pygame.display.flip()

    # Resolution was determined experimentally on the first 101 seeds to find the minimum number to find all squares
    def get_visible_squares(self, eye: Tuple[int, int], resolution: int =1) -> List[Tuple[int, int]]:
        targets = []
        for i in range(0, self.width * resolution):
            targets.append((0, i / resolution))
            targets.append((29, i / resolution))
        for i in range(0, self.height * resolution):
            targets.append((i / resolution, 0))
            targets.append((i / resolution, 29))
        targets = list(set(targets))

        visible_squares = set([])

        for target in targets:
            dx = target[0] - eye[0]
            dy = target[1] - eye[1]
            nx = abs(dx)
            ny = abs(dy)
            sign_x = 1 if dx > 0 else -1
            sign_y = 1 if dy > 0 else -1

            p = list(eye)
            points = [tuple(p)]
            ix = 0
            iy = 0
            while ix < nx or iy < ny:
                decision = (1 + 2 * ix) * ny - (1 + 2 * iy) * nx
                if decision == 0:
                    # check if either corner is not a wall
                    corners = [list(p), list(p)]
                    corners[0][0] += sign_x
                    corners[1][1] += sign_y
                    if (self.board_states[corners[0][0], corners[0][1]] == self.WALL and
                            self.board_states[corners[1][0], corners[1][1]] == self.WALL):
                        break
                    if self.board_states[corners[0][0], corners[0][1]] != self.WALL:
                        visible_squares.add(tuple(corners[0]))
                    if self.board_states[corners[1][0], corners[1][1]] != self.WALL:
                        visible_squares.add(tuple(corners[1]))
                    p[0] += sign_x
                    p[1] += sign_y
                    if self.board_states[p[0], p[1]] == self.WALL:
                        break
                    visible_squares.add(tuple(p))
                    ix += 1
                    iy += 1
                elif decision < 0:
                    p[0] += sign_x
                    if self.board_states[p[0], p[1]] == self.WALL:
                        break
                    visible_squares.add(tuple(p))
                    ix += 1
                else:
                    p[1] += sign_y
                    if self.board_states[p[0], p[1]] == self.WALL:
                        break
                    visible_squares.add(tuple(p))
                    iy += 1
        return list(visible_squares)


# The rest of this code is to remove later. I don't think there is anything useful left here
    # def is_visible(self, eye, target):
    #     squares = consistent_raytrace(eye, target)
    #     # print(target, eye, squares)
    #     for square in squares:
    #         if self.board_states[square[0], square[1]] == self.WALL:
    #             return False
    #     return True
    #
    # # Trash implementation rn does not do anything good
    # def is_visible_four(self, eye, target):
    #     for i in range(5):
    #         new_target_x = Fraction(target[0]) + Fraction(49, 100) if i == 0 or i == 1 else Fraction(-49, 100)
    #         new_target_y = Fraction(target[1]) + Fraction(49, 100) if i == 0 or i == 2 else Fraction(-49, 100)
    #         new_target_x = target[0] if i == 4 else new_target_x
    #         new_target_y = target[1] if i == 4 else new_target_y
    #         if self.is_visible_integrated(eye, (new_target_x, new_target_y)):
    #             return True
    #     return False
    #
    # def is_visible_integrated(self, eye, target):
    #     dx = target[0] - eye[0]
    #     dy = target[1] - eye[1]
    #     nx = abs(dx)
    #     ny = abs(dy)
    #     sign_x = 1 if dx > 0 else -1
    #     sign_y = 1 if dy > 0 else -1
    #
    #     p = list(eye)
    #     points = [tuple(p)]
    #     ix = 0
    #     iy = 0
    #     while ix < nx or iy < ny:
    #         decision = (1 + 2 * ix) * ny - (1 + 2 * iy) * nx
    #         if decision == 0:
    #             # check if either corner is not a wall
    #             corners = [list(p), list(p)]
    #             corners[0][0] += sign_x
    #             corners[1][1] += sign_y
    #             if (self.board_states[corners[0][0], corners[0][1]] == self.WALL and
    #                     self.board_states[corners[1][0], corners[1][1]] == self.WALL):
    #                 return False
    #             p[0] += sign_x
    #             p[1] += sign_y
    #             ix += 1
    #             iy += 1
    #         elif decision < 0:
    #             p[0] += sign_x
    #             ix += 1
    #         else:
    #             p[1] += sign_y
    #             iy += 1
    #         if self.board_states[p[0], p[1]] == self.WALL:
    #             return False
    #     return True


# https://www.redblobgames.com/grids/line-drawing.html
# Ensures not seeing through any walls, but cannot see on diagonal if one of the walls is blocked, which is not ideal
# Might need to integrate the ray trace in with the board state in order to allow us to see if one of the blocks in the
# diagonal is not there, this could also terminate early when trying the ray cast between the two for better
# performance?
# def consistent_raytrace(v0, v1):
#     dx = v1[0] - v0[0]
#     dy = v1[1] - v0[1]
#     nx = abs(dx)
#     ny = abs(dy)
#     sign_x = 1 if dx > 0 else -1
#     sign_y = 1 if dy > 0 else -1
#
#     p = list(v0)
#     points = [tuple(p)]
#     ix = 0
#     iy = 0
#     while ix < nx or iy < ny:
#         decision = (1 + 2 * ix) * ny - (1 + 2 * iy) * nx
#         if decision == 0:
#             temp_p = list(p)
#             temp_p[0] += sign_x
#             points.append(tuple(temp_p))
#             p[1] += sign_y
#             points.append(tuple(p))
#             p[0] += sign_x
#             points.append(tuple(p))
#             ix += 1
#             iy += 1
#         elif decision < 0:
#             p[0] += sign_x
#             points.append(tuple(p))
#             ix += 1
#         else:
#             p[1] += sign_y
#             points.append(tuple(p))
#             iy += 1
#     return points
#
#
# def vector_raytrace(v0, v1):
#     # The equation of the ray is v = v0 + t*d
#     v1 = np.array(v1, dtype=np.float64)
#     v0 = np.array(v0, dtype=np.float64)
#     d = v1 - v0
#     d[d == 0] = 0.000000000001
#     inc = np.sign(d + Fraction())  # Gives the quadrant in which the ray progress
#
#     # Rounding coordinates give us the current tile
#     tile = np.array(np.round(v0), dtype=int)
#     tiles = [tuple(tile)]
#     v = v0
#     endtile = np.array(np.round(v1), dtype=int)
#
#     # Continue as long as we are not in the last tile
#     while np.max(np.abs(endtile - v)) > 0.5:
#         # L = (Lx, Ly) where Lx is the x coordinate of the next vertical
#         # line and Ly the y coordinate of the next horizontal line
#         L = tile + Fraction(1, 2) * inc
#
#         # Solve the equation v + d*t == L for t, simultaneously for the next
#         # horizontal line and vertical line
#         t = (L - v) / d
#
#         if t[0] == t[1]:
#             temp = tile
#             temp[0] += inc[0]
#             tiles.append(tuple(temp))
#             tile[1] += inc[1]
#             v += t[1] * d
#         elif t[1] == np.nan or t[0] < t[1]:  # The vertical line is intersected first
#             # print("test1", tile)
#             tile[0] += inc[0]
#             # print("test2", tile)
#             v += t[0] * d
#         else:  # The horizontal line is intersected first
#             tile[1] += inc[1]
#             v += t[1] * d
#         # print("test3", tile)
#         tiles.append(tuple(tile))
#
#     return tiles
