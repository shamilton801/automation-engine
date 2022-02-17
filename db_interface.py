from io import TextIOWrapper

class DBInterface:
    SEEKER = 1
    HIDER = 0

    def __init__(self):
        pass

    def get_opponents(self, type):
        raise NotImplementedError()

    def download_bot_file(self, name, type, destinaton):
        raise NotImplementedError()

    def get_real_name(self, filename):
        raise NotImplementedError()