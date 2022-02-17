from db_interface import DBInterface
import requests
import shutil
import os

class FirebaseDBInterface(DBInterface):
    """
    Interface for firebase

    download_bot_file: 
    """
    
    def __init__():
        super().__init__()

    def configure(self, record):
        self.player = {}
        self.player.name = record["name"]
        self.player.filename = record["filename"]
        self.player.type = DBInterface.SEEKER if record["type"] == "seeker" else DBInterface.HIDER
        self.player.link = record["link"] 

        self.opponents = {}
        for r in record["opponents"]:
            self.opponents[r["name"]] =  (r["filename"], r["link"])    

    def get_opponents(self, type):
        result = []
        for filename, _ in self.opponents:
            result.append(filename)
        
        return result
        

    def download_bot_file(self, name, type, destination):
        if type == self.player.type:
            url = self.player.link   
        else:
            url = self.opponents[name]
        
        r = requests.get(url)
        with open(os.path.join(destination, f"{name}.py"), 'wb') as f:
            f.write(r.content) 