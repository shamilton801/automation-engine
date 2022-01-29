import docker
import uuid

client = docker.from_env()

class Match:
    def __init__(self, bot1, bot2):
        self._bot1 = bot1
        self._bot2 = bot2
        self._container = None
        self._result_file_name = self._get_hash()
    
    def run(self):
        self.container = client.containers.run("img", self._bot1, self._bot2, self._result_file_name)
    
    def stop(self):
        self.container.kill()

    def is_finished(self):
        return self.container.status == "exited"

    def get_results(self):
        cat_exit_code, cat_output = self.container.exec_run("cat " + self._result_file_name)
        return cat_output

    def _get_hash(self):
        return str(uuid.uuid1())
