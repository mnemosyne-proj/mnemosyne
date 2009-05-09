#
# mnemosyne_test.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class MnemosyneTest:
    
    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"))

    def teardown(self):
        self.mnemosyne.finalise()
        
