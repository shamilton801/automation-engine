from io import TextIOWrapper

class DBInterface:
    SEEKER = 1
    HIDER = 2

    def __init__(self):
        pass

    def get_opponents(self, type):
        raise NotImplementedError()

    def get_bot_file(self, name, type) -> TextIOWrapper:
        raise NotImplementedError()