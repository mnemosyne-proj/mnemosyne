#
# test_main_controller.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.dialogs import *
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

save_file = ""

class Widget(MainWidget):

    def save_file_dialog(self, path, filter, caption=""):
        return save_file
    
    def open_file_dialog(self, path, filter, caption=""):
        return os.path.join(os.getcwd(), "dot_test", "default.db")

class TestMainController(MnemosyneTest):

    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_main_controller", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "AddCardsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "EditCardDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "BrowseCardsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "CardAppearanceDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ActivatePluginsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ManageCardTypesDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "StatisticsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ConfigurationDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ActivateCardsDialog"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()
        
    def test_coverage(self):
        global save_file
        os.path.join(os.getcwd(), "dot_test", "copy.db")
        
        self.controller().heartbeat()
        self.controller().add_cards()
        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.review_controller().new_question()        
        self.controller().edit_current_card()        
        self.controller().file_new()
        self.controller().file_open()
        self.controller().file_save_as()
        self.controller().card_appearance()        
        self.controller().activate_plugins()  
        self.controller().manage_card_types()        
        self.controller().browse_cards()
        self.controller().configure()
        self.controller().show_statistics()
        self.controller().activate_cards()
        
    def test_2(self):
        self.controller().file_save_as()
        self.controller().file_open()

    def test_overwrite(self):
        global save_file
        os.path.join(os.getcwd(), "dot_test", "default.db")

        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.controller().file_save()
        
        self.controller().file_new()
