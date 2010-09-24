#
# test_client.py <Peter.Bienstman@UGent.be>
#

PORT = 6666

import subprocess
subprocess.Popen(["./bin/python", "./mnemosyne/UDP_server/server.py"])

import time
time.sleep(1)

import socket

class Client(object):

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(("localhost", PORT))

    def send_command(self, command):
        self.socket.send(command)
        f = self.socket.makefile("rb")
        line = f.readline()
        while line != "DONE\n":
            print line
            # If it's a callback command, we need to act upon it immediately,
            # either because the other side is waiting for input from us, or
            # for efficiency reasons, e.g. if the controller says it's already
            # OK to update a widget, best to do it now and not wait for the
            # entire command to finish.
            if line.startswith("< "):
                if "mnemosyne.main_widget().show_question" in line:
                    self.send_answer(0)
            line = f.readline()

    def send_answer(self, data):
        self.socket.send(str(data) + "\n")

c = Client()

import os
data_dir = os.path.abspath("dot_mnemosyne2")
filename = "default.db"

c.send_command("mnemosyne.initialise(data_dir=\"%s\", filename=\"%s\", automatic_upgrades=False)\n" % (data_dir, filename))
c.send_command("mnemosyne.start_review()" + "\n")
c.send_command("mnemosyne.main_widget().show_question(\"a\", \"1\", \"2\", \"3\")" + "\n")            
c.send_command("mnemosyne.review_widget().show_answer()" + "\n")
