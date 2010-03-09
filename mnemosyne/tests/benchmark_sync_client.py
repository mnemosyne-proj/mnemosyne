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
        # Do 200 reviews.
        card_type = self.mnemosyne.card_type_by_id("1")
        fact_data = {"q": "question",
                     "a": "answer"}
        card = self.mnemosyne.controller().create_new_cards(fact_data, card_type,
                grade=-1, tag_names=["default"])[0]
        self.mnemosyne.database().save()
        self.mnemosyne.review_controller().new_question()
        for i in range(200):
            self.mnemosyne.review_controller().show_answer()
            self.mnemosyne.review_controller().grade_answer(0)
        Client.__init__(self, self.mnemosyne.database(),
                        self.mnemosyne.main_widget())
        
    def do_sync(self):
        self.sync("http://127.0.0.1:8185", "user", "pass")
        self.mnemosyne.database().save()

client = MyClient()

import time
t1 = time.time()
    
def sync():
    client.do_sync()

sync()
print time.time() - t1

tests = []#["sync()"]

for test in tests:
    cProfile.run(test, "mnemosyne_profile." + test.replace("()", ""))
    print
    print "*** ", test, " ***"
    print
    p = pstats.Stats('mnemosyne_profile.' + test.replace("()", ""))
    p.strip_dirs().sort_stats('cumulative').print_stats(number_of_calls)
    
