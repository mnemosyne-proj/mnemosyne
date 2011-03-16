#
# test_main_controller.py <Peter.Bienstman@UGent.be>
#

import os
from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.dialogs import *
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

save_file = ""

class Widget(MainWidget):

    def get_filename_to_save(self, path, filter, caption=""):
        return save_file
    
    def get_filename_to_open(self, path, filter, caption=""):
        return os.path.join(os.getcwd(), "dot_test", "default.db")


class TestMainController(MnemosyneTest):

    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
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
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "SyncDialog"))
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
        self.controller().show_add_cards_dialog()
        card_type = self.card_type_by_id("2")
        fact_data = {"f": "f", "b": "b"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.review_controller().new_question()        
        self.controller().show_edit_card_dialog()        
        self.controller().show_new_file_dialog()
        self.controller().show_open_file_dialog()
        self.controller().show_save_file_as_dialog()
        self.controller().show_card_appearance_dialog()        
        self.controller().show_activate_plugins_dialog()  
        self.controller().show_manage_card_types_dialog()        
        self.controller().show_browse_cards_dialog()
        self.controller().show_configuration_dialog()
        self.controller().show_statistics_dialog()
        self.controller().show_activate_cards_dialog()
        self.controller().download_source()
        self.controller().sync()
        
    def test_2(self):
        self.controller().show_save_file_as_dialog()
        self.controller().show_open_file_dialog()

    def test_overwrite(self):
        global save_file
        os.path.join(os.getcwd(), "dot_test", "default.db")

        card_type = self.card_type_by_id("2")
        fact_data = {"f": "f", "b": "b"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.controller().save_file()
        
        self.controller().show_new_file_dialog()

    def test_coverage(self):
        from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
        w = MainWidget(self.mnemosyne.component_manager)
        w.show_information("")
        w.show_error("")
        w.set_status_bar_message("")

        self.controller().show_add_cards_dialog()
        self.controller().show_edit_card_dialog()
        self.controller().show_insert_video_dialog("")        
        self.controller().show_download_source_dialog()
        self.controller().show_sync_dialog()
        self.controller().show_card_appearance_dialog()
        self.controller().show_activate_plugins_dialog()
        self.controller().show_manage_card_types_dialog()
        self.controller().show_statistics_dialog()
        self.controller().show_configuration_dialog()
        self.controller().show_browse_cards_dialog()
        self.controller().show_activate_cards_dialog()
        self.controller().show_import_file_dialog()
        self.controller().show_export_file_dialog()
        self.controller().heartbeat()
