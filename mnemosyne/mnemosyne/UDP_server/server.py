#
# server.py <Peter.Bienstman@UGent.be>
#

import SocketServer

from mnemosyne.libmnemosyne import Mnemosyne


class MyHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "> " + data
        
        mnemosyne = self.server.mnemosyne
        # Hijack the component manager to store some more global data there.
        mnemosyne.component_manager.socket = socket
        mnemosyne.component_manager.client_address = self.client_address       

        exec(data)


class Server(SocketServer.UDPServer):

    def __init__(self, port):

        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0,
            ("mnemosyne.libmnemosyne.translator", "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.UDP_server.UDP_main_window",
             "UDP_MainWindow"))
        self.mnemosyne.components.append(\
            ("mnemosyne.UDP_server.UDP_review_widget",
             "UDP_ReviewWidget"))
        
        SocketServer.UDPServer.__init__(self, ("localhost", port), MyHandler)

        print "Server listening on port", port
        self.serve_forever()


if __name__ == "__main__":
    server = Server(6666)




