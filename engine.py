from multiprocessing import Queue, Process
from db_interface import DBInterface
from match import Match
from test_db_interface import TestDBInterface
import time

# Parameters
MAX_CON_MATCHES = 1

# Enums
SEEKER = 1
HIDER = 2

class Engine:

    def __init__(self, db: DBInterface):
        self._running_matches = []
        self._matches_to_run = Queue()
        self._stop_flag = False
        self._db = db

    def handle_new_bot(self, bot_name, type):
        opponents = self._db.get_opponents(type)
        for opp in opponents:
            self._matches_to_run.put(Match(bot_name, opp, time.time(), self._db))

    def stop(self):
        self._stop_flag = True
        self._consumer_handle.join()

    def start(self):
        if self._stop_flag:
            self._consumer_handle = Process(target=self._match_consumer, args=(self,))
            self._consumer_handle.start()
            self._stop_flag = False

    def _match_consumer(self):
        while not self._stop_flag:
            if len(self._running_matches) < MAX_CON_MATCHES:
                new_match = self._matches_to_run.get()
                new_match.run()
                self._running_matches.append(new_match)

            for match in self._running_matches:
                if match.is_finished():
                    json_result = match.get_result()
                    self._send_result(json_result)
                    self._running_matches.remove(match)

    def _send_result(self, json_result):
        print(json_result)

if __name__ == '__main__':
    db = TestDBInterface()
    engine = Engine(db)
    engine.start()
    engine.handle_new_bot("seeker", DBInterface.SEEKER)
    engine.handle_new_bot("hider", DBInterface.HIDER)
    engine.handle_new_bot("scotland_yard", DBInterface.SEEKER)