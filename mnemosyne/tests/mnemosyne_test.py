#
# mnemosyne_test.py <Peter.Bienstman@UGent.be>
#

import os
import shutil

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget

class TestReviewWidget(ReviewWidget):

    def redraw_now(self):
        pass


class MnemosyneTest():
    
    def setup(self):
        shutil.rmtree("dot_test", ignore_errors=True)
        self.restart()

    def restart(self):
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"),
                                  automatic_upgrades=False)
        self.mnemosyne.start_review()

    def teardown(self):
        self.mnemosyne.finalise()

    def config(self):
        return self.mnemosyne.component_manager.current("config")

    def log(self):
        return self.mnemosyne.component_manager.current("log")

    def database(self):
        return self.mnemosyne.component_manager.current("database")

    def scheduler(self):
        return self.mnemosyne.component_manager.current("scheduler")

    def main_widget(self):
        return self.mnemosyne.component_manager.current("main_widget")

    def review_widget(self):
        return self.mnemosyne.component_manager.current("review_widget")

    def controller(self):
        return self.mnemosyne.component_manager.current("controller")

    def review_controller(self):
        return self.mnemosyne.component_manager.current("review_controller")

    def card_types(self):
        return self.mnemosyne.component_manager.all("card_type")

    def filters(self):
        return self.mnemosyne.component_manager.all("filter")

    def plugins(self):
        return self.mnemosyne.component_manager.all("plugin")

    def render_chain(self, id="default"):
        return self.mnemosyne.component_manager.render_chain_by_id[id]  

    def card_type_by_id(self, id): 
        return self.mnemosyne.component_manager.card_type_by_id[id]

        
