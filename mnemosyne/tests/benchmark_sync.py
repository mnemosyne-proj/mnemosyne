#!/usr/bin/env python

import os
import time
import pstats
import cProfile

from mnemosyne.libmnemosyne import Mnemosyne

number_of_calls = 150 # Number of calls to display in profile
number_of_facts = 6000

mnemosyne = None


from threading import Thread

from openSM2sync.server import Server
from openSM2sync.client import Client
from openSM2sync.log_entry import EventTypes

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class Widget(MainWidget):
    
    def status_bar_message(self, message):
        print message
        
    def information_box(self, info):
        print info
        
    def error_box(self, error):
        print error

        
class MyServer(Server, Thread):

    program_name = "Mnemosyne"
    program_version = "test"
    capabilities = "TODO"

    stop_after_sync = True

    def __init__(self):
        Thread.__init__(self)
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("test_sync", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ProgressDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
     
    def authorise(self, login, password):
        return login == "user" and password == "pass"

    def open_database(self, database_name):
        self.database = self.mnemosyne.database()

    def run(self):
        # We only open the database connection inside the thread to prevent
        # access problems, as a single connection can only be used inside a
        # single thread.
        self.mnemosyne.initialise(os.path.abspath("sync_from_here"))
        self.mnemosyne.review_controller().reset()
        Server.__init__(self, "127.0.0.1", 8161, self.mnemosyne.main_widget())
        # Because we stop_after_sync is True, serve_forever will actually stop
        # after one sync.
        self.serve_forever()
        self.mnemosyne.finalise()


class MyClient(Client):
    
    program_name = "Mnemosyne"
    program_version = "test"
    capabilities = "TODO"
    
    def __init__(self):
        os.system("rm -fr dot_benchmark")
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("test_sync", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ProgressDialog"))
        self.mnemosyne.initialise(os.path.abspath(os.path.join(os.getcwdu(),
                                  "dot_benchmark")))
        self.mnemosyne.review_controller().reset()        
        Client.__init__(self, self.mnemosyne.database(),
                        self.mnemosyne.main_widget())
        
    def do_sync(self):
        self.sync("http://127.0.0.1:8161", "user", "pass")


def sync():
    server = MyServer()    
    server.start()
    client = MyClient()
    client.do_sync()


sync()

tests = ["sync()"]

for test in []:#tests:  
    cProfile.run(test, "mnemosyne_profile." + test.replace("()", ""))
    print
    print "*** ", test, " ***"
    print
    p = pstats.Stats('mnemosyne_profile.' + test.replace("()", ""))
    p.strip_dirs().sort_stats('cumulative').print_stats(number_of_calls)
    
