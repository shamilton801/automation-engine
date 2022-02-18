import sys
import datetime

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
   
    def write(self, message):
        self.terminal.write(message)
        with open("logfile.log", "a") as f:
            f.write(f"{datetime.datetime.now()}\t{message}")  

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()