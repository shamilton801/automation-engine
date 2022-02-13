from threading import Thread, Lock, Event
from db_interface import DBInterface
from collections import deque
from match import Match
from test_db_interface import TestDBInterface
import docker
import time
import sys

# Parameters
MAX_CON_MATCHES = 10

class Engine:

    def __init__(self, db: DBInterface, stop_event: Event):
        self._running_matches:Match = []
        self._matches_to_run = deque()
        self._stop_event = stop_event
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
        self._stop_event.set()
        self._consumer_handle.join()
        self._stop_event.clear()

    def start(self):
        self._consumer_handle = Thread(target=self._match_consumer, args=(), daemon=True)
        self._consumer_handle.start()

    def _match_consumer(self):
        while not self._stop_event.is_set():
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

        for match in self._running_matches:
            match.stop()

    def _send_result(self, json_result):
        print(json_result)


count = 1
def keyboard_loop():
    global count
    while True:
        try:
            pass
        except KeyboardInterrupt:
            print(f"Ctrl-C Received {count}/2")
            count += 1
            break

if __name__ == '__main__':
    db = TestDBInterface()
    engine = Engine(db, Event())
    engine.start()
    engine.handle_new_bot("seeker", DBInterface.SEEKER)
    engine.handle_new_bot("hider", DBInterface.HIDER)
    engine.handle_new_bot("scotland_yard", DBInterface.SEEKER)
    
    keyboard_loop()
    engine.stop()
    docker.from_env().containers.prune()
    keyboard_loop()            

