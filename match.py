from time import time
from tkinter.ttk import _TreeviewColumnDict
import docker
import uuid
import os

from db_interface import DBInterface

client = docker.from_env()

class Match:
    def __init__(self, bot1, bot2, timestamp, db: DBInterface):
        self._bot1 = bot1
        self._bot2 = bot2
        self._timestamp = timestamp
        self._container = None
        self._result_file_name = self._get_hash()
        self._db = db
    
    def run(self):
        parent_dir = os.path.dirname(__file__)
        full_path = os.path.join(parent_dir, str(self._timestamp))
        os.mkdir(full_path)
        
        bot1file = self._db.get_bot_file(self._bot1)
        bot2file = self._db.get_bot_file(self._bot2)

        command = f"python game.py {self._bot1}.py {self._bot2}.py {self._result_file_name}"
        self.container = client.containers.run("python",
                                               command=command,
                                               detach=True,
                                               volumes=["./code:/code"],
                                               network_disabled=True,
                                               mem_limit="500m",
                                               cpu_count=1,
                                               )        
                    
    def stop(self):
        self.container.kill()

    def is_finished(self):
        return self.container.status == "exited"

    def get_results(self):
        cat_exit_code, cat_output = self.container.exec_run("cat " + self._result_file_name)
        return cat_output

    def _get_hash(self):
        return str(uuid.uuid1())
