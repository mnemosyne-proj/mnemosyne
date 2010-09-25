#
# test_client.py <Peter.Bienstman@UGent.be>
#

PORT = 6666

import os
import time
import socket
import subprocess

data_dir = os.path.abspath("dot_mnemosyne2")
filename = "default.db"

subprocess.Popen(["./bin/python", "./mnemosyne/UDP_server/server.py",
    str(PORT)])


class Client(object):

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(("localhost", PORT))
        connected = False
        while not connected:
            try:
                self.send_command("print 'hi'")
                connected = True
            except:
                time.sleep(0.1)

    def send_command(self, command):
        # The print commands are just for demonstration here, and should not
        # be there in a 'real' client.
        print ">>" + command
        self.socket.send(command + "\n")
        f = self.socket.makefile("rb")
        line = f.readline()
        while line != "DONE\n":
            print line
            # If it's a callback command, we need to act upon it immediately,
            # either because the other side is waiting for input from us, or
            # for efficiency reasons, e.g. if the controller says it's already
            # OK to update a widget, best to do it now and not wait for the
            # entire command to finish.
            if line.startswith("@@"):
                if "main_widget.show_question" in line:
                    self.send_answer(0) # Hardcoded option 0.
                # Handle all the other callbacks:
                # ...
            line = f.readline()

    def send_answer(self, data):
        self.socket.send(str(data) + "\n")


c = Client()
c.send_command("mnemosyne.initialise(data_dir=\"%s\", filename=\"%s\")" % (data_dir, filename))
c.send_command("mnemosyne.start_review()")
c.send_command("mnemosyne.main_widget().show_question(\"a\", \"1\", \"2\", \"3\")")            
c.send_command("mnemosyne.review_widget().show_answer()")
c.send_command("mnemosyne.finalise()")
c.send_command("exit()")
