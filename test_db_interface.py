from db_interface import DBInterface
import os

class TestDBInterface(DBInterface):
    def __init__(self):
        super().__init__(self)


    def _get_test_bot_dir(self, type):
        file_path = None
        if type == super().SEEKER:
            file_path = "./test/test_seekers"
        elif type == super().HIDER:
            file_path = "./test/test_hiders"
        else:
            raise Exception("Bad opponent type")

        return file_path

    def get_opponents(self, type):
        file_names = os.listdir(self._get_test_bot_dir(type))
        for i, name in enumerate(file_names):
            file_names[i] = name.split('.')[0]

        return file_names

    def get_bot_file(self, name, type):
        return open(self._get_test_bot_dir(type) + f"/{name}.py")

        
        

