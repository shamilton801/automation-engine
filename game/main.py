import time

from board import Board
import sys
import json
from game import Game
from hider import Hider
from seeker import Seeker

count = 0
valid_seeds = [1, 2, 5, 6, 7, 8, 11, 12, 14, 16, 19, 20, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32, 35, 38, 39, 41, 43, 45,
               47, 48, 49, 51, 53, 55, 62, 63, 67, 69, 70, 71, 72, 75, 77, 79, 81, 82, 84, 86, 87, 90, 91, 92, 93, 95,
               96, 97, 99, 101, 103, 107, 108, 112, 113, 114, 115, 117, 121, 122, 123, 128, 129, 131, 132, 134, 135,
               138, 139, 146, 149, 153, 155, 157, 159, 161, 163, 166, 167, 168, 170, 171, 172, 175, 179, 181, 184, 190,
               191, 192, 196, 198, 199]

seeker_points = 0
hider_points = 0


for i, seed in enumerate(valid_seeds):
    print(f"------------- Match {i} -------------")
    start = time.time()
    game = Game(Hider(), Seeker(), seed)
    winner, timesteps = game.game_loop()
    seeker_points += game.max_turns - timesteps
    hider_points += timesteps
    finish_time = time.time()
    print("Total time (sec):", finish_time - start)
    print(f"winner: {winner}\tturn count: {timesteps}")
    print(f"seconds/turn: {(finish_time - start)/timesteps:.3f}")

result = {
    "seeker_points": seeker_points,
    "hider_points": hider_points,
    "extra_info": ""
}

result_file_name = sys.argv[2]
with open(f"{result_file_name}.json") as f:
    json_str = json.dumps(result)
    f.write(json_str)