import os

from openSM2sync.server import Server
from openSM2sync.client import Client
from threading import Thread
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class Widget(MainWidget):
    
    def status_bar_message(self, message):
        print message
        
    def error_box(self, error):
        print error
        
    def question_box(self, question, option0, option1, option2):
        if option0 == "&Delete":
            return 0
        raise NotImplementedError
    
        
class ServerThread(Thread):

    def run(self):
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("test", "Widget"))
        self.mnemosyne.initialise(os.path.abspath(os.path.join(os.getcwdu(), "dot_mnemosyne_server")))
        url = "http://127.0.0.1:8024"
        server = Server(url, self.mnemosyne.database(), self.mnemosyne.main_widget())
        server.start()
        self.mnemosyne.finalise()


class ClientThread(Thread):

    def run(self):

        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("test", "Widget"))
        self.mnemosyne.initialise(os.path.abspath(os.path.join(os.getcwdu(), "dot_mnemosyne_client")))
        url = "http://user:pass@127.0.0.1:8024"
        client = Client(url, self.mnemosyne.database(),
                        self.mnemosyne.main_widget())
        client.start()
        self.mnemosyne.finalise()                             

if __name__ == "__main__":
    server_thread = ServerThread()
    server_thread.start()
    client_thread = ClientThread()
    client_thread.start()    
    #server_thread.join()
