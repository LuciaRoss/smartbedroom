import time

class Logger:

    def __init__(self):
        self.logfile = "assistant.log"

    def log(self, text):
        with open(self.logfile, 'a') as f:
            toprint = time.strftime("%c") + "   -   " + text+"\n"
            f.write(toprint)



