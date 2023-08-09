#
# test_controller.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil
from pytest import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.dialogs import *
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.ui_components.dialogs import ExportDialog
from mnemosyne.libmnemosyne.ui_components.dialogs import ExportMetadataDialog

save_file = ""

answer = None

class Widget(MainWidget):

    def get_filename_to_save(self, path, filter, caption=""):
        return save_file

    def get_filename_to_open(self, path, filter, caption=""):
        return os.path.join(os.getcwd(), "dot_test", "default.db")

    def show_question(self, question, option0, option1, option2):
        return answer

class DataWidget(ExportMetadataDialog):

    def values(self):
        return {}

class ExportWidget(ExportDialog):

    pass



class TestController(MnemosyneTest):

    def setup_method(self):
        self.initialise_data_dir()
        path = os.path.join(os.getcwd(), "..", "mnemosyne", "libmnemosyne",
                            "renderers")
        if path not in sys.path:
            sys.path.append(path)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
            ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("test_controller", "Widget"))
        self.mnemosyne.components.append(\
            ("test_controller", "ExportWidget"))
        self.mnemosyne.components.append(\
            ("test_controller", "DataWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "AddCardsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "EditCardDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "BrowseCardsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "SyncDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ManagePluginsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ManageCardTypesDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "StatisticsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ConfigurationDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ActivateCardsDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ImportDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "TipDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "GettingStartedDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "AboutDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "CompactDatabaseDialog"))

        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()

    def test_coverage(self):
        global save_file
        os.path.join(os.getcwd(), "dot_test", "copy.db")

        self.controller().heartbeat()
        self.controller().show_add_cards_dialog()
        card_type = self.card_type_with_id("2")
        fact_data = {"f": "f", "b": "b"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.review_controller().show_new_question()
        self.controller().show_edit_card_dialog()
        self.controller().show_new_file_dialog()
        self.controller().show_open_file_dialog()
        self.controller().show_save_file_as_dialog()
        self.controller().show_compact_database_dialog()
        self.controller().show_manage_plugins_dialog()
        self.controller().show_manage_card_types_dialog()
        self.controller().show_browse_cards_dialog()
        self.controller().show_configuration_dialog()
        self.controller().show_statistics_dialog()
        self.controller().show_activate_cards_dialog()
        self.controller().show_tip_dialog()
        self.controller().show_getting_started_dialog()
        self.controller().show_about_dialog()
        self.controller().show_download_source_dialog()
        self.controller().show_sync_dialog()

    def test_star(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "f", "b": "b"}
        card = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])[0]
        self.review_controller().show_new_question()
        self.controller().star_current_card()
        card = self.database().card(card._id, is_id_internal=True)
        assert "Starred" in card.tag_string()

    def test_2(self):
        self.controller().show_save_file_as_dialog()
        self.controller().show_open_file_dialog()

    def test_overwrite(self):
        global save_file
        os.path.join(os.getcwd(), "dot_test", "default.db")

        card_type = self.card_type_with_id("2")
        fact_data = {"f": "f", "b": "b"}
        card_1, card_2 = self.controller().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.controller().save_file()

        self.controller().show_new_file_dialog()

    def test_coverage_2(self):
        from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
        w = MainWidget(self.mnemosyne.component_manager)
        w.show_information("")
        w.show_error("")
        w.set_status_bar_message("")

        self.controller().show_add_cards_dialog()
        self.controller().show_edit_card_dialog()
        self.controller().show_insert_sound_dialog("")
        self.controller().show_insert_video_dialog("")
        self.controller().show_insert_flash_dialog("")
        self.controller().show_download_source_dialog()
        self.controller().show_sync_dialog()
        self.controller().show_manage_plugins_dialog()
        self.controller().show_manage_card_types_dialog()
        self.controller().show_statistics_dialog()
        self.controller().show_configuration_dialog()
        self.controller().show_browse_cards_dialog()
        self.controller().show_activate_cards_dialog()
        self.controller().show_import_file_dialog()
        self.controller().show_export_file_dialog()
        self.controller().next_rollover = 0
        self.controller().heartbeat()

    def test_delete_current(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "1"}
        self.controller().create_new_cards(fact_data, card_type, grade=-1, tag_names=[])
        fact_data = {"f": "2", "b": "2"}
        self.controller().create_new_cards(fact_data, card_type, grade=-1, tag_names=[])
        self.review_controller().show_new_question()
        self.review_controller().grade_answer(0)
        self.review_controller().grade_answer(0)
        self.review_controller().grade_answer(2)
        global answer
        answer = 0
        self.controller().delete_current_card()

    def test_delete_current_2(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "1", "b": "1"}
        self.controller().create_new_cards(fact_data, card_type, grade=-1, tag_names=[])
        fact_data = {"f": "2", "b": "2"}
        self.controller().create_new_cards(fact_data, card_type, grade=-1, tag_names=[])
        self.review_controller().show_new_question()
        self.review_controller().grade_answer(0)
        self.review_controller().grade_answer(0)
        self.review_controller().grade_answer(0)
        self.review_controller().grade_answer(2)
        global answer
        answer = 0
        self.controller().delete_current_card()

    def test_retain_only_child_tags(self):
        c = self.controller()
        assert c._retain_only_child_tags(["a"]) == ["a"]
        assert sorted(c._retain_only_child_tags(["a", "b"])) == sorted(["a", "b"])
        assert c._retain_only_child_tags(["a", "a::b"]) == ["a::b"]
        assert c._retain_only_child_tags(["a", "a::b", "a::b::c"]) == ["a::b::c"]
        assert c._retain_only_child_tags(["a", "a::b::c"]) == ["a::b::c"]
        assert c._retain_only_child_tags(["a::b", "a::b::c"]) == ["a::b::c"]
        assert c._retain_only_child_tags(["a::b::c"]) == ["a::b::c"]
