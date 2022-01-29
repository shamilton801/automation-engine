from multiprocessing import Queue, Process
from match import Match

MAX_CON_MATCHES = 1

class Engine:

    def __init__(self):
        self._running_matches = []
        self._matches_to_run = Queue()
        self._consumer_handle = Process(target=self._match_consumer, args=(self,))
        self._consumer_handle.start()
        self._stop_flag = False

    def handle_new_bot(self, bot_name, type):
        opponents = get_opponents(type)
        for opp in opponents:
            self._matches_to_run.put(Match(bot_name, opp))

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
        pass