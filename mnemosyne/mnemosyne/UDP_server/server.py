#
# server.py <Peter.Bienstman@UGent.be>
#

import sys
import select
import socketserver

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.utils import traceback_string


class OutputCatcher:

    def __init__(self, socket):
        self.socket = socket

    def write(self, data):
        self.socket.sendall(data)
        

class MyHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        socket.connect(self.client_address)
        sys.stdout = sys.stderr = OutputCatcher(socket)
        # We use the component manager to store some more global data there.
        mnemosyne = self.server.mnemosyne
        mnemosyne.component_manager.socket = socket
        if data != "exit()":
            try:
                exec(data)
            except:
                socket.sendall("__EXCEPTION__\n" + traceback_string())
        else:
            self.server.stopped = True
        socket.sendall("__DONE__\n")


class Server(socketserver.UDPServer):

    def __init__(self, port, upload_science_logs=False,
                 interested_in_old_reps=False):
        self.mnemosyne = Mnemosyne(upload_science_logs, interested_in_old_reps)
        self.mnemosyne.components.insert(0,
            ("mnemosyne.libmnemosyne.translator", "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.UDP_server.main_wdgt",
             "MainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.UDP_server.review_wdgt",
             "ReviewWdgt"))    
        socketserver.UDPServer.__init__(self, ("localhost", port), MyHandler)
        print(("Server listening on port", port))
        self.stopped = False
        while not self.stopped:
            # We time out every 0.25 seconds, so that changing
            # self.stopped can have an effect.
            if select.select([self.socket], [], [], 0.25)[0]:
                self.handle_request()
        self.socket.close()


if __name__ == "__main__":
    port = int(sys.argv[1])
    server = Server(port)




