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

    """This is a very simple client illustrating the basic structure of
    an UDP client. Also consult 'How to write a new frontend' in the docs
    of libmnemosyne for more information about the interaction between
    libmnemosyne and a frontend.

    """

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(("localhost", PORT))
        connected = False
        while not connected:
            try:
                self.send_command("# Waiting for server...")
                connected = True
            except:
                time.sleep(0.1)

    def send_command(self, command):
        # The print commands are just for demonstration here, and should not
        # be there in a 'real' client.
        print ">>" + command
        self.socket.send(command + "\n")
        # Parse the reply.
        f = self.socket.makefile("rb")
        line = f.readline()
        while line != "__DONE__\n":
            print line,
            # If it's a callback command, we need to act upon it immediately,
            # either because the other side is waiting for input from us, or
            # for efficiency reasons, e.g. if the controller says it's already
            # OK to update a widget, best to do it now and not wait for the
            # entire command to finish.
            if line.startswith("@@"):
                if "main_widget.show_question" in line:
                    # Normally, we should ask the user which option he
                    # chooses, but here we just hard-code option 0.
                    self.send_answer(0)
                # Handle all the other callbacks:
                # ...
            # Simplistic error handling: just print out traceback, which runs
            # until the final "__DONE__".
            elif line.startswith("__EXCEPTION__"):
                traceback_lines = []
                traceback_lines.append(f.readline())
                while traceback_lines[-1] != "__DONE__\n":
                    traceback_lines.append(f.readline())
                print "".join(traceback_lines[:-1])
                break
            # Read the next line and act on that.
            line = f.readline()
            
    def send_answer(self, data):
        self.socket.send(str(data) + "\n")


c = Client()
c.send_command("mnemosyne.initialise(data_dir=\"%s\", filename=\"%s\")" % (data_dir, filename))
c.send_command("mnemosyne.start_review()")
c.send_command("mnemosyne.review_controller().show_answer()")
c.send_command("mnemosyne.review_controller().grade_answer(0)")
c.send_command("mnemosyne.finalise()")

c.send_command("mnemosyne.main_widget().show_question(\"a\", \"1\", \"2\", \"3\")")
c.send_command("1/0")

c.send_command("exit()")
