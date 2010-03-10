#!/usr/bin/env python

import os
import time
import pstats
import cProfile

from mnemosyne.libmnemosyne import Mnemosyne

number_of_calls = 20 # Number of calls to display in profile
number_of_facts = 6000

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

        
class MyServer(Server):

    program_name = "Mnemosyne"
    program_version = "test"
    capabilities = "TODO"

    stop_after_sync = True

    def __init__(self):
        os.system("rm -rf sync_from_here")
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("test_sync", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ProgressDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("sync_from_here"))
        self.mnemosyne.review_controller().reset()
        # Add 20 cards to database.
        card_type = self.mnemosyne.card_type_by_id("1")
        for i in range (20):
            fact_data = {"q": "question %d" % (i,),
                         "a": "answer"}
            self.mnemosyne.controller().create_new_cards(fact_data, card_type,
                grade=-1, tag_names=["default"])[0]
        self.mnemosyne.database().save()
     
    def authorise(self, login, password):
        return login == "user" and password == "pass"

    def open_database(self, database_name):
        self.database = self.mnemosyne.database()

    def run(self):
        Server.__init__(self, "192.168.2.54", 8186, self.mnemosyne.main_widget())
        # Because we stop_after_sync is True, serve_forever will actually stop
        # after one sync.
        self.serve_forever()
        self.mnemosyne.finalise()

server = MyServer()

import time
t1 = time.time()
               
def run():  
    server.run()

run()
print time.time() - t1

tests = [] #["run()"]

for test in tests:  
    cProfile.run(test, "mnemosyne_profile." + test.replace("()", ""))
    print
    print "*** ", test, " ***"
    print
    p = pstats.Stats('mnemosyne_profile.' + test.replace("()", ""))
    p.strip_dirs().sort_stats('cumulative').print_stats(number_of_calls)
    
