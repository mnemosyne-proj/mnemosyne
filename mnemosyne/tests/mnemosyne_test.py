#
# mnemosyne_test.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne import Mnemosyne

class MnemosyneTest:
    
    def setup(self):
        os.system("rm -fr dot_test")
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.initialise(os.path.abspath("dot_test"))

    def teardown(self):
        self.mnemosyne.finalise()
        
