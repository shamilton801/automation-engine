from db_interface import DBInterface
import shutil
import os

class TestDBInterface(DBInterface):
    def __init__(self):
        super().__init__()


    def _get_test_bot_dir(self, type):
        file_path = None
        parent_dir = os.path.dirname(__file__)
        if type == super().SEEKER:
            file_path = os.path.join(parent_dir, "test", "test_seekers")
        elif type == super().HIDER:
            file_path = os.path.join(parent_dir, "test", "test_hiders")
        else:
            raise Exception("Bad opponent type")

        return file_path

    def get_opponents(self, type):
        file_names = os.listdir(self._get_test_bot_dir(1 - type))
        for i, name in enumerate(file_names):
            file_names[i] = name.split('.')[0]

        return file_names

    def download_bot_file(self, name, type, destination):
        source_loc = os.path.join(self._get_test_bot_dir(type), f"{name}.py")
        if type == super().SEEKER:
            shutil.copy(source_loc, os.path.join(destination, "seeker.py"))
        elif type == super().HIDER:
            shutil.copy(source_loc, os.path.join(destination, "hider.py"))
        else:
            raise Exception("bad bot type:", type)