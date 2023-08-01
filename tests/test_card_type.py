#
# test_card_type.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.libmnemosyne.fact_view import FactView
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

last_error = None

class Widget(MainWidget):

    def show_error(self, error):
        global last_error
        last_error = error



class DecoratedThreeSided(CardType):

    id = "3_decorated"
    name = "Foreign word with pronunciation (decorated)"

    # List and name the keys.
    fact_keys_and_names = [("f", "Foreign word"),
              ("p_1", "Pronunciation"),
              ("m_1", "Translation")]

    # Recognition.
    v1 = FactView("Recognition", "3.1")
    v1.q_fact_keys = ["f"]
    v1.a_fact_keys = ["p_1", "m_1"]
    v1.q_fact_key_decorators = {"f": "What is the translation of ${f}?"}

    # Production.
    v2 = FactView("Production", "3.2")
    v2.q_fact_keys = ["m_1"]
    v2.a_fact_keys = ["f", "p_1"]
    v2.q_fact_key_decorators = {"m_1": "How do you say ${t}?"}

    fact_views = [v1, v2]
    unique_fact_keys = ["f"]
    required_fact_keys = ["f", "m_1"]

class TestCardType(MnemosyneTest):

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
            ("test_card_type", "DecoratedThreeSided"))
        self.mnemosyne.components.append(\
            ("test_card_type", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()

    def test_card_types(self):
        card_type = self.card_type_with_id("1")
        assert self.database().is_in_use(card_type) is False
        assert card_type.fact_key_with_name("Front") == "f"
        assert card_type.is_fact_data_valid({"f": "foo"}) == True
        assert self.card_type_with_id("1") == self.card_type_with_id("1")
        assert self.card_type_with_id("1") != None

    def test_database(self):
        card_type = self.card_type_with_id("1")
        card_type.fact_views[0].type_answer = True
        card_type.fact_views[0].extra_data = {"b": "b"}
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        card_type.extra_data = {"b": "b"}
        self.database().update_card_type(card_type)
        self.mnemosyne.component_manager.unregister(card_type)
        card_type_out = self.database().card_type(card_type.id,
                                                      is_id_internal=False)
        assert card_type_out.id == "1::1 clone"
        assert card_type_out.fact_key_with_name("Front") == "f"
        assert card_type_out.required_fact_keys == ["f"]
        assert card_type_out.is_fact_data_valid({"f": "foo"}) == True
        assert card_type_out.is_fact_data_valid({"q": "foo"}) == False
        assert card_type_out.fact_key_names() == ["Front", "Back"]

        assert card_type_out.fact_keys_and_names == card_type.fact_keys_and_names
        assert card_type_out.unique_fact_keys == card_type.unique_fact_keys
        assert card_type_out.keyboard_shortcuts == card_type.keyboard_shortcuts
        assert card_type_out.fact_views[0].type_answer == True
        assert card_type_out.fact_views[0].extra_data == {"b": "b"}
        assert card_type_out.extra_data == {"b": "b"}
        assert len(card_type.fact_views) == 1
        assert len(card_type_out.fact_views) == 1
        assert card_type_out.fact_views[0].id == \
               card_type.fact_views[0].id
        assert card_type_out.fact_views[0].name == \
               card_type.fact_views[0].name
        assert card_type_out.fact_views[0].q_fact_keys == \
               card_type.fact_views[0].q_fact_keys
        assert card_type_out.fact_views[0].a_fact_keys == \
               card_type.fact_views[0].a_fact_keys
        assert card_type_out.fact_views[0].a_on_top_of_q == \
               card_type.fact_views[0].a_on_top_of_q

        # Reset global variables.
        self.mnemosyne.component_manager.register(card_type)
        card_type = self.card_type_with_id("1")
        card_type.fact_views[0].type_answer = False
        card_type.fact_views[0].extra_data = {}

        card_type_orig = self.database().card_type("1",
                                                      is_id_internal=False)
        assert card_type_orig.fact_views[0].type_answer == False

    def test_rename_two_clones(self):
        card_type = self.card_type_with_id("1")
        card_type_1 = self.controller().clone_card_type(\
            card_type, "1 clone")
        card_type = self.card_type_with_id("2")
        card_type_2 = self.controller().clone_card_type(\
                      card_type, "2 clone")

        self.controller().rename_card_type(card_type_1, "1 clone new")

        assert set([c.name for c in self.card_types() if \
            self.database().is_user_card_type(c)]) == \
            set(["1 clone new", "2 clone"])

    def test_rename_two_clones_b(self):
        card_type = self.card_type_with_id("1")
        card_type_1 = self.controller().clone_card_type(\
            card_type, "1 clone")
        card_type = self.card_type_with_id("2")
        card_type_2 = self.controller().clone_card_type(\
                      card_type, "2 clone")

        self.controller().rename_card_type(card_type_2, "2 clone new")

        assert set([c.name for c in self.card_types() if \
            self.database().is_user_card_type(c)]) == \
            set(["1 clone", "2 clone new"])

    def test_delete(self):
        card_type = self.card_type_with_id("1")
        card_type_1 = self.controller().clone_card_type(\
            card_type, "1 clone")
        card_type = self.card_type_with_id("2")
        card_type_2 = self.controller().clone_card_type(\
                      card_type, "2 clone")

        self.controller().delete_card_type(card_type_1)

        card_type_out = self.database().card_type(card_type_2.id,
            is_id_internal=False)

        assert card_type_out.fact_views[0].id == \
               card_type_2.fact_views[0].id
        assert card_type_out.fact_views[0].name == \
               card_type_2.fact_views[0].name
        assert card_type_out.fact_views[0].q_fact_keys == \
               card_type_2.fact_views[0].q_fact_keys
        assert card_type_out.fact_views[0].a_fact_keys == \
               card_type_2.fact_views[0].a_fact_keys
        assert card_type_out.fact_views[0].a_on_top_of_q == \
               card_type_2.fact_views[0].a_on_top_of_q
        assert card_type_out.fact_views[1].id == \
               card_type_2.fact_views[1].id
        assert card_type_out.fact_views[1].name == \
               card_type_2.fact_views[1].name
        assert card_type_out.fact_views[1].q_fact_keys == \
               card_type_2.fact_views[1].q_fact_keys
        assert card_type_out.fact_views[1].a_fact_keys == \
               card_type_2.fact_views[1].a_fact_keys
        assert card_type_out.fact_views[1].a_on_top_of_q == \
               card_type_2.fact_views[1].a_on_top_of_q

    def test_delete_with_formatting(self):
        card_type = self.card_type_with_id("1")
        card_type_1 = self.controller().clone_card_type(\
            card_type, "1 clone")
        card_type = self.card_type_with_id("2")
        card_type_2 = self.controller().clone_card_type(\
                      card_type, "2 clone")

        self.config().set_card_type_property("background_colour", "black", card_type_1)

        self.controller().delete_card_type(card_type_1)

    def test_cannot_delete(self):
        global last_error
        last_error = None

        card_type = self.card_type_with_id("1")
        self.controller().delete_card_type(card_type)
        assert "in use" in last_error
        last_error = None

        card_type_1 = self.controller().clone_card_type(\
            card_type, "1 clone")
        card_type = self.card_type_with_id("2")
        card_type_2 = self.controller().clone_card_type(\
                      card_type, "2 clone")
        fact_data = {"f": "question",
                     "b": "answer"}
        old_card = self.controller().create_new_cards(fact_data, card_type_1,
                                 grade=-1, tag_names=["default"])[0]
        self.controller().delete_card_type(card_type_1)
        assert "in use" in last_error
        last_error = None

    def test_rename(self):
        card_type = self.card_type_with_id("1")
        card_type_1 = self.controller().clone_card_type(\
            card_type, "1 clone")
        self.controller().rename_card_type(card_type_1, "newname")
        card_type_out = self.database().card_type(card_type_1.id,
            is_id_internal=False)
        assert card_type_out.name == "newname"

    def test_cannot_rename(self):
        global last_error
        last_error = None
        card_type = self.card_type_with_id("1")
        self.controller().rename_card_type(card_type, "newname")
        assert last_error.startswith("Cannot rename")
        last_error = None

    def test_cannot_rename_duplicate(self):
        global last_error
        last_error = None
        card_type = self.card_type_with_id("1")
        card_type_1 = self.controller().clone_card_type(\
            card_type, "1 clone")
        self.controller().rename_card_type(card_type_1, "Vocabulary")
        assert "in use" in last_error
        last_error = None

    def test_has_clones(self):
        global last_error
        last_error = None
        card_type = self.card_type_with_id("1")
        assert self.database().has_clones(card_type) == False
        card_type_1 = self.controller().clone_card_type(\
            card_type, "1 clone")
        card_type_2 = self.controller().clone_card_type(\
            card_type_1, "1 clone clone")
        assert self.database().has_clones(card_type) == True
        assert self.database().has_clones(card_type_1) == True
        self.controller().delete_card_type(card_type_1)
        assert "clone" in last_error
        last_error = None

    def test_clone_of_clone(self):
        card_type = self.card_type_with_id("1")
        assert self.database().is_user_card_type(card_type) == False
        card_type.fact_views[0].type_answer = True
        card_type.fact_views[0].extra_data = {"b": "b"}
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        assert self.database().is_user_card_type(card_type) == True
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone cloned"))
        assert self.database().is_user_card_type(card_type) == True
        card_type.extra_data = {"b": "b"}
        self.database().update_card_type(card_type)
        assert self.render_chain().renderer_for_card_type(card_type) is not None
        self.mnemosyne.component_manager.unregister(card_type)
        card_type_out = self.database().card_type(card_type.id,
                                                      is_id_internal=False)
        assert card_type_out.fact_key_with_name("Front") == "f"
        assert card_type_out.required_fact_keys == ["f"]
        assert card_type_out.is_fact_data_valid({"f": "foo"}) == True

        assert card_type_out.fact_keys_and_names == card_type.fact_keys_and_names
        assert card_type_out.unique_fact_keys == card_type.unique_fact_keys
        assert card_type_out.keyboard_shortcuts == card_type.keyboard_shortcuts
        assert card_type_out.fact_views[0].type_answer == True
        assert card_type_out.fact_views[0].extra_data == {"b": "b"}
        assert card_type_out.extra_data == {"b": "b"}
        assert len(card_type.fact_views) == 1
        assert len(card_type_out.fact_views) == 1
        assert card_type_out.fact_views[0].id == \
               card_type.fact_views[0].id
        assert card_type_out.fact_views[0].name == \
               card_type.fact_views[0].name
        assert card_type_out.fact_views[0].q_fact_keys == \
               card_type.fact_views[0].q_fact_keys
        assert card_type_out.fact_views[0].a_fact_keys == \
               card_type.fact_views[0].a_fact_keys
        assert card_type_out.fact_views[0].a_on_top_of_q == \
               card_type.fact_views[0].a_on_top_of_q

        # Reset global variables.
        self.mnemosyne.component_manager.register(card_type)
        card_type.fact_views[0].type_answer = False
        card_type.fact_views[0].extra_data = {}

        fact_data = {"f": "question",
                     "b": "answer"}
        card = self.mnemosyne.controller().create_new_cards(fact_data, card_type,
           grade=-1, tag_names=["default"])[0]
        path = self.mnemosyne.database().path()
        self.mnemosyne.database().unload()
        self.mnemosyne.database().load(path)

    def test_decorators(self):
        fact_data = {"f": "foreign word",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        card_type = self.card_type_with_id("3_decorated")
        card = self.controller().create_new_cards(fact_data, card_type,
                  grade=-1, tag_names=["default"])[0]
        assert "What is the translation of foreign word?" in card.question()

    def test_properties(self):
        card_type = self.card_type_with_id("1")
        self.config().set_card_type_property("font", "myfont", card_type)
        self.config().set_card_type_property("background_colour", "mycolour", card_type)
        card_type = self.controller().clone_card_type(\
            card_type, ("1 clone"))
        assert self.config().card_type_property("font", card_type, 'f') == "myfont"
        assert self.config().card_type_property("background_colour", card_type) == "mycolour"
