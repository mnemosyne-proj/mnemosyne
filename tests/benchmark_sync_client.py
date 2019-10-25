#!/usr/bin/env python

import os
import time
import pstats
import shutil
import cProfile

from mnemosyne.libmnemosyne import Mnemosyne

number_of_calls = 50 # Number of calls to display in profile
number_of_facts = 6000

from openSM2sync.server import Server
from openSM2sync.client import Client
from openSM2sync.log_entry import EventTypes

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget

class Widget(MainWidget):

    def set_progress_text(self, text):
        print(text)

    def show_information(self, info):
        print(info)

    def show_error(self, error):
        print(error)

class MyReviewWidget(ReviewWidget):

    def redraw_now(self):
        pass


class MyClient(Client):

    program_name = "Mnemosyne"
    program_version = "test"
    capabilities = "TODO"

    def __init__(self):
        shutil.rmtree(os.path.abspath("dot_sync_client"), ignore_errors=True)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
        self.mnemosyne.components = [
            ("mnemosyne.libmnemosyne.gui_translator",
             "NoGuiTranslation"),
            ("mnemosyne.libmnemosyne.databases.SQLite",
             "SQLite"),
            ("mnemosyne.libmnemosyne.configuration",
             "Configuration"),
            ("mnemosyne.libmnemosyne.loggers.database_logger",
             "DatabaseLogger"),
            ("mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne",
             "SM2Mnemosyne"),
            ("mnemosyne.libmnemosyne.stopwatch",
             "Stopwatch"),
            ("mnemosyne.libmnemosyne.card_types.front_to_back",
             "FrontToBack"),
            ("mnemosyne.libmnemosyne.card_types.both_ways",
             "BothWays"),
            ("mnemosyne.libmnemosyne.card_types.vocabulary",
             "Vocabulary"),
            ("mnemosyne.libmnemosyne.renderers.html_css",
             "HtmlCss"),
            ("mnemosyne.libmnemosyne.filters.escape_to_html",
             "EscapeToHtml"),
            ("mnemosyne.libmnemosyne.filters.expand_paths",
             "ExpandPaths"),
            ("mnemosyne.libmnemosyne.filters.latex",
             "Latex"),
            ("mnemosyne.libmnemosyne.render_chains.default_render_chain",
             "DefaultRenderChain"),
            ("mnemosyne.libmnemosyne.render_chains.plain_text_chain",
             "PlainTextChain"),
            ("mnemosyne.libmnemosyne.controllers.default_controller",
             "DefaultController"),
            ("mnemosyne.libmnemosyne.review_controllers.SM2_controller",
             "SM2Controller"),
            ("mnemosyne.libmnemosyne.card_types.map",
             "MapPlugin"),
            ("mnemosyne.libmnemosyne.card_types.cloze",
             "ClozePlugin"),
            ("mnemosyne.libmnemosyne.criteria.default_criterion",
             "DefaultCriterion"),
            ("mnemosyne.libmnemosyne.databases.SQLite_criterion_applier",
             "DefaultCriterionApplier"),
            ("mnemosyne.libmnemosyne.plugins.cramming_plugin",
             "CrammingPlugin") ]
        self.mnemosyne.components.append(("benchmark_sync_client", "Widget"))
        self.mnemosyne.components.append(("benchmark_sync_client", "MyReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath(os.path.join(os.getcwd(),
                                  "dot_sync_client")), automatic_upgrades=False)
        self.mnemosyne.config().change_user_id("user_id")
        self.check_for_edited_local_media_files = False
        self.do_backup = False
        self.mnemosyne.review_controller().reset()
        # Do 200 reviews.
        card_type = self.mnemosyne.card_type_with_id("1")
        fact_data = {"f": "question",
                     "b": "answer"}
        card = self.mnemosyne.controller().create_new_cards(fact_data, card_type,
                grade=-1, tag_names=["default"])[0]
        self.mnemosyne.database().save()
        self.mnemosyne.review_controller().show_new_question()
        for i in range(200):
            self.mnemosyne.review_controller().show_answer()
            self.mnemosyne.review_controller().grade_answer(0)
        Client.__init__(self, "client_machine_id", self.mnemosyne.database(),
                        self.mnemosyne.main_widget())

    def do_sync(self):
        #self.BUFFER_SIZE = 10*8192
        #self.behind_proxy = True
        self.sync("localhost", 8186, "user", "pass")
        self.mnemosyne.database().save()

if __name__== '__main__':

    client = MyClient()

    def sync():
        client.do_sync()

    tests = ["sync()"]

    for test in tests:
        cProfile.run(test, "mnemosyne_profile." + test.replace("()", ""))
        print()
        print(("*** ", test, " ***"))
        print()
        p = pstats.Stats('mnemosyne_profile.' + test.replace("()", ""))
        p.strip_dirs().sort_stats('cumulative').print_stats(number_of_calls)
