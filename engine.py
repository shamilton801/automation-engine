from threading import Thread, Lock
from db_interface import DBInterface
from collections import deque
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
        self._running_matches:Match = []
        self._matches_to_run = deque()
        self._stop_flag = False
        self._db = db
        self._lock = Lock()

    def handle_new_bot(self, bot_name, type):
        opponents = self._db.get_opponents(type)
        for opp in opponents:
            new_match = Match(bot_name, opp, type, time.time(), self._db)
            self._lock.acquire()
            self._matches_to_run.appendleft(new_match)
            self._lock.release()

    def stop(self):
        self._stop_flag = True
        self._consumer_handle.join()
        self._stop_flag = False

    def start(self):
        self._consumer_handle = Thread(target=self._match_consumer, args=())
        self._consumer_handle.start()
        self._stop_flag = False

    def _match_consumer(self):
        while not self._stop_flag:
            if len(self._running_matches) < MAX_CON_MATCHES and len(self._matches_to_run) > 0:
                self._lock.acquire()
                new_match = self._matches_to_run.pop()
                self._lock.release()
                new_match.run()
                self._running_matches.append(new_match)

            for match in self._running_matches:
                if match.is_finished():
                    json_result = match.get_result()
                    print(json_result)
                    self._send_result(json_result)
                    self._running_matches.remove(match)

    def _send_result(self, json_result):
        print(json_result)

if __name__ == '__main__':
    db = TestDBInterface()
    engine = Engine(db)
    try:
        engine.start()
        engine.handle_new_bot("seeker", DBInterface.SEEKER)
        engine.handle_new_bot("hider", DBInterface.HIDER)
        engine.handle_new_bot("scotland_yard", DBInterface.SEEKER)
    except KeyboardInterrupt:
        engine.stop()
        