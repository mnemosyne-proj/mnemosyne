#
# test_main_controller.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.dialogs import *

class TestMainController(MnemosyneTest):

    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_cramming", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "AddCardsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "EditFactDialog"))
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
        self.mnemosyne.initialise(os.path.abspath("dot_test"))

    def test_coverage(self):
        self.ui_controller_main().heartbeat()
        self.ui_controller_main().add_cards()
        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.ui_controller_main().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.ui_controller_review().new_question()        
        self.ui_controller_main().edit_current_card()        
        self.ui_controller_main().file_new()
        self.ui_controller_main().file_open()
        self.ui_controller_main().file_save_as()
        self.ui_controller_main().card_appearance()        
        self.ui_controller_main().activate_plugins()  
        self.ui_controller_main().manage_card_types()        
        self.ui_controller_main().browse_cards()
        self.ui_controller_main().configure()
        self.ui_controller_main().show_statistics()
