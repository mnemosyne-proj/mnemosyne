import os

from openSM2sync.server import Server
from openSM2sync.client import Client
from threading import Thread
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class Widget(MainWidget):
    
    def status_bar_message(self, message):
        print message
        
    def information_box(self, info):
        print info
        
    def error_box(self, error):
        print error
        
    def question_box(self, question, option0, option1, option2):
        if option0 == "&Delete":
            return 0
        raise NotImplementedError
    
        
class ServerThread(Thread):

    def authorise(self, login, password):
        return login == "user" and password == "pass"

    def run(self):
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("test", "Widget"))
        self.mnemosyne.initialise(os.path.abspath(os.path.join(os.getcwdu(), "dot_mnemosyne_server")))
        self.server = Server("127.0.0.1", 8024,
                             self.mnemosyne.database(), self.mnemosyne.main_widget())
        self.server.authorise = self.authorise
        self.server.serve_forever()
        self.mnemosyne.finalise()


class ClientObject(object):

    def start(self):

        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("test", "Widget"))
        self.mnemosyne.initialise(os.path.abspath(os.path.join(os.getcwdu(), "dot_mnemosyne_client")))
        url = "http://127.0.0.1:8024"
        client = Client(self.mnemosyne.database(), self.mnemosyne.main_widget())
        client.sync(url, "user", "pass")
        self.mnemosyne.finalise()                             

if __name__ == "__main__":
    try:
        server_thread = ServerThread()
        server_thread.start()
        client = ClientObject()
        client.start()
    except:
        import traceback, sys
        traceback.print_exc(file=sys.stdout)
    server_thread.server.stop()
    server_thread.join(0)
    print 'closing down server'
    server_thread.server.socket.close() 
