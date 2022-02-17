import docker
import uuid
import os
import json

from db_interface import DBInterface

class Match:

    ERRORDRAW = 0
    BOT1 = 1
    BOT2 = 2

    def __init__(self, bot1, bot2, type, timestamp, db: DBInterface):
        self._bot1 = bot1
        self._bot1_type = type
        self._bot2 = bot2
        self._bot2_type = Match.inverse_type(type)
        
        self._timestamp = int(timestamp*100000)
        self._result_file_name = self._get_hash()
        self._db = db
        self._parent_dir = os.path.dirname(__file__)
        self._client = docker.from_env()
    
    def inverse_type(type):
        return 1-type

    def run(self):
        match_dir_path = os.path.join(self._parent_dir, f"temp", f"match_{str(self._timestamp)}")
        os.mkdir(match_dir_path)
        
        self._db.download_bot_file(self._bot1, self._bot1_type, match_dir_path)
        self._db.download_bot_file(self._bot2, self._bot2_type, match_dir_path)

        seeker = self._bot1 if self._bot1_type == DBInterface.SEEKER else self._bot2
        hider = self._bot2 if self._bot2_type == DBInterface.HIDER else self._bot1
        command = f"python -m cyberchase {seeker} {hider} {self._result_file_name}"

        try:
            self._container = self._client.containers.run("python",
                                                          command=command,
                                                          detach=True,
                                                          volumes=[f"{match_dir_path}:/code"],
                                                          network_disabled=True,
                                                          mem_limit="1000m",
                                                          cpu_count=1,
                                                          )        
        except docker.errors.ContainerError as e: 
            print("Code execution failed - syntax error")
            print(e)
                    
    def stop(self):
        self._container.kill()

    def is_finished(self):
        self._container.reload()
        res = self._container.status == "exited"
        return res

    def get_result(self):
        full_path = os.path.join(self._parent_dir, "temp", f"match_{self._timestamp}", f"{self._result_file_name}.json")
        with open(full_path) as jsonf:
            result = json.load(jsonf)
            seeker = self._bot1 if self._bot1_type == DBInterface.SEEKER else self._bot2
            hider =  self._bot1 if self._bot1_type == DBInterface.HIDER else self._bot2
            result["seeker"] = seeker
            result["hider"] = hider
        return result

    def _get_hash(self):
        return str(uuid.uuid1())
