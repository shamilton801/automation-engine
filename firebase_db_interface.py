from db_interface import DBInterface
import requests
import shutil
import os

class FirebaseDBInterface(DBInterface):
    """
    Interface for firebase

    download_bot_file: 
    """
    
    def __init__(self):
        super().__init__()

    def configure(self, record):
        self._player = {}
        self._player.name = record["name"]
        self._player.filename = record["filename"].rsplit(".", 1)[0]
        self._player.type = DBInterface.SEEKER if record["type"] == "seeker" else DBInterface.HIDER
        self._player.link = record["link"] 

        self._opponents = {}
        for r in record["opponents"]:
            self._opponents[r["name"]] =  (r["filename"].rsplit(".", 1)[0], r["link"])    

    def get_opponents(self, type):
        result = []
        for filename, _ in self._opponents:
            result.append(filename)
        
        return result
        

    def download_bot_file(self, name, type, destination):
        if type == self._player.type:
            url = self._player.link   
        else:
            url = self._opponents[name]
        
        r = requests.get(url)
        with open(os.path.join(destination, f"{name}.py"), 'wb') as f:
            f.write(r.content) 

    def get_real_name(self, filename):
        if filename == self._player.filename:
            return self._player.name
        else:
            for name, t in self._opponents.items():
                if t[0] == filename:
                    return name

        raise Exception(f"Could not find bot name mapped to {filename}.py")