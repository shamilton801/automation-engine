import time
import sys
import json
from game import Game, SeekerException, HiderException
from hider import Hider
from seeker import Seeker

class Match:
    def __init__(self):
        self._count = 0
        self._valid_seeds = [1, 2, 5, 6, 7, 8, 11, 12, 14, 16, 19, 20, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32, 35, 38, 39, 41, 43, 45,
                    47, 48, 49, 51, 53, 55, 62, 63, 67, 69, 70, 71, 72, 75, 77, 79, 81, 82, 84, 86, 87, 90, 91, 92, 93, 95,
                    96, 97, 99, 101, 103, 107, 108, 112, 113, 114, 115, 117, 121, 122, 123, 128, 129, 131, 132, 134, 135,
                    138, 139, 146, 149, 153, 155, 157, 159, 161, 163, 166, 167, 168, 170, 171, 172, 175, 179, 181, 184, 190,
                    191, 192, 196, 198, 199]

        self._seeker_points = 0
        self._hider_points = 0
        self._seeker_errors = 0
        self._hider_errors = 0
        self._seeker_info = []
        self._hider_info = []


    def run(self):
        for i, seed in enumerate(self._valid_seeds):
            print(f"------------- Game {i} -------------")
            try:
                hider = Hider()
            except Exception:
                self._hider_errors += 1
                continue
        
            try: 
                seeker = Seeker()
            except Exception:
                self._seeker_errors += 1
                continue

            try:            
                start = time.time()
                game = Game(hider, seeker, seed, render=False)
                winner, timesteps = game.game_loop()
                self._seeker_points += game.max_turns - timesteps
                self._hider_points += timesteps
                finish_time = time.time()
            except SeekerException as e:
                self._seeker_errors += 1
                self._seeker_info.append(f"Game {i}, Seed {self._valid_seeds[i]}, {e}")
            except HiderException as e:
                self._hider_errors += 1
                self._hider_info.append(f"Game {i}, Seed {self._valid_seeds[i]}, {e}")

            print("Total time (sec):", finish_time - start)
            print(f"winner: {winner}\tturn count: {timesteps}")
            print(f"seconds/turn: {(finish_time - start)/timesteps:.3f}")

    def get_result(self):
        result = {
            "seeker_points": self._seeker_points,
            "hider_points": self._hider_points,
            "seeker_errors": self._seeker_errors,
            "hider_errors": self._hider_errors,
            "seeker_info": '\n'.join(self._seeker_info),
            "hider_info": '\n'.join(self._hider_info),
        }
        return result

if __name__ == '__main__':
    match = Match()
    match.run()
    result_file_name = sys.argv[1]
    with open(f"{result_file_name}.json", "w") as f:
        json_str = json.dumps(match.get_result())
        f.write(json_str)