#!/usr/bin/env python

import os
import sys
import time
import pstats
import shutil
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

    def set_progress_text(self, message):
        print(message)
        #sys.stderr.write(message+'\n')

    def show_information(self, info):
        print(info)
        #sys.stderr.write(info+'\n')

    def show_error(self, error):
        global last_error
        last_error = error
        # Activate this for debugging.
        sys.stderr.write(error)


class MyServer(Server):

    program_name = "Mnemosyne"
    program_version = "test"
    capabilities = "TODO"

    def __init__(self):
        shutil.rmtree(os.path.abspath("dot_sync_server"), ignore_errors=True)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.gui_translator",
            "GetTextGuiTranslator"))
        self.mnemosyne.components.append(("test_sync", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_sync_server"), automatic_upgrades=False)
        self.mnemosyne.config().change_user_id("user_id")
        self.mnemosyne.review_controller().reset()
        self.supports_binary_transfer = lambda x : False
        # Add 20 cards to database.
        card_type = self.mnemosyne.card_type_with_id("1")
        for i in range (20):
            fact_data = {"f": "question %d" % (i,),
                         "b": "answer"}
            self.mnemosyne.controller().create_new_cards(fact_data, card_type,
                grade=-1, tag_names=["default"])[0]
        self.mnemosyne.database().save()
        self.mnemosyne.database().release_connection()

    def authorise(self, login, password):
        return login == "user" and password == "pass"

    def load_database(self, database_name):
        self.mnemosyne.database().load(database_name)
        return self.mnemosyne.database()

    def unload_database(self, database):
        self.mnemosyne.database().release_connection()
        # Dirty way to make sure we restart the server and create a new database
        # (as opposed to keep sending old history back and forth)'
        self.wsgi_server.stop()

    def run(self):
        Server.__init__(self, "client_machine_id", 8186,
                        self.mnemosyne.main_widget())
        self.serve_until_stopped()

server = MyServer()

def run():
    server.run()

tests = ["run()"]

for test in tests:
    cProfile.run(test, "mnemosyne_profile." + test.replace("()", ""))
    print()
    print(("*** ", test, " ***"))
    print()
    p = pstats.Stats('mnemosyne_profile.' + test.replace("()", ""))
    p.strip_dirs().sort_stats('cumulative').print_stats(number_of_calls)

