#
# server.py <Peter.Bienstman@UGent.be>
#

import os
import threading
import SocketServer

from mnemosyne.libmnemosyne import Mnemosyne


class MnemosyneThread(threading.Thread):

    def __init__(self, data_dir, filename):
        threading.Thread.__init__(self)
        self.data_dir = data_dir
        self.filename = filename

    def run(self):
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0,
            ("mnemosyne.libmnemosyne.translator", "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.UDP_server.UDP_main_window",
             "UDP_MainWindow"))
        self.mnemosyne.components.append(\
            ("mnemosyne.UDP_server.UDP_review_widget",
             "UDP_ReviewWidget"))
        self.mnemosyne.initialise(self.data_dir, self.filename,
            automatic_upgrades=False)
        # The next calls will be executed in the handler thread, so we release
        # the database connection
        self.mnemosyne.database().release_connection()


class MyHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "> " + data
        
        mnemosyne = self.server.thread.mnemosyne
        exec(data)

        # Wait for buffer lock?
        
        socket.sendto(mnemosyne.main_widget().buffer, self.client_address)
        mnemosyne.main_widget().buffer = ""


class Server(SocketServer.UDPServer):

    def __init__(self, port, data_dir, filename):

        self.thread = MnemosyneThread(data_dir, filename)
        self.thread.start()
        
        SocketServer.UDPServer.__init__(self, ("localhost", port), MyHandler)

        print "Serving", os.path.join(data_dir, filename)
        print "Server listening on port", port
        self.serve_forever()


if __name__ == "__main__":
    data_dir = os.path.abspath("dot_mnemosyne2")
    filename = "default.db"
    server = Server(6666, data_dir, filename)




