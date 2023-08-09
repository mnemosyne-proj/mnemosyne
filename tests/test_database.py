#
# test_database.py <Peter.Bienstman@UGent.be>
#

import datetime
import os
import sys
import shutil
import time

from openSM2sync.log_entry import EventTypes

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

HOUR = 60 * 60  # Seconds in an hour.
DAY = 24 * HOUR  # Seconds in a day.

answer = None


class Widget(MainWidget):

    def show_question(self, question, option0, option1, option2):
        #sys.stderr.write(question+'\n')
        if question.startswith("Identical card is already in database"):
            return answer
        else:
            print(question)
            raise NotImplementedError


class TestDatabase(MnemosyneTest):

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
            ("test_database", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()

    def test_release(self):
        self.database().release_connection()
        self.database().release_connection()
        self.database().display_name()
        self.database().abandon()
        self.database().new("default.mem")

    def test_tags(self):
        tag = Tag("test")
        self.database().add_tag(tag)
        assert len(self.database().tags()) == 2
        assert self.database().tags()[0].name == "test"
        tag.name = "test2"
        self.database().update_tag(tag)
        assert len(self.database().tags()) == 2
        assert self.database().tags()[0].name == "test2"

    def test_tag_order(self):
        tag = Tag("a")
        self.database().add_tag(tag)
        tag = Tag("1. a")
        self.database().add_tag(tag)
        assert [tag.name for tag in self.database().tags()] == ["1. a", "a", "__UNTAGGED__"]

    def test_new_cards(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        old_card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["default"])[0]
        assert len([self.database().cards()]) == 1

        old_fact = old_card.fact
        self.database().unload()

        self.database().load(self.config()["last_database"])
        assert self.database().fact_count() == 1
        card = self.database().card(old_card._id, is_id_internal=True)
        fact = card.fact

        assert fact.data["f"] == "question"
        assert fact.data["b"] == "answer"
        assert fact.id == old_fact.id
        assert [tag.name for tag in card.tags] == \
               [tag.name for tag in old_card.tags]

        assert card.fact == old_card.fact
        assert card.fact_view == old_card.fact_view
        assert card.id == old_card.id
        assert card.creation_time == old_card.creation_time
        assert card.modification_time == old_card.modification_time
        assert card.grade == old_card.grade
        assert card.easiness == old_card.easiness
        assert card.acq_reps == old_card.acq_reps
        assert card.ret_reps == old_card.ret_reps
        assert card.lapses == old_card.lapses
        assert card.acq_reps_since_lapse == old_card.acq_reps_since_lapse
        assert card.last_rep == old_card.last_rep
        assert card.next_rep == old_card.next_rep
        assert card.extra_data == old_card.extra_data
        assert card.scheduler_data == old_card.scheduler_data
        assert card.active == old_card.active

        # Modify cards

        card.grade = -1
        card.easiness = -2
        card.acq_reps = -3
        card.ret_reps = -4
        card.lapses = -5
        card.acq_reps_since_lapse = -6
        card.last_rep = -7
        card.next_rep = -8
        card.extra_data = "extra"
        card.scheduler_data = 1
        card.in_view = False

        self.database().update_card(card)
        new_card = list(self.database().cards_from_fact(fact))[0]

        assert card.grade == -1
        assert card.easiness == -2
        assert card.acq_reps == -3
        assert card.ret_reps == -4
        assert card.lapses == -5
        assert card.acq_reps_since_lapse == -6
        assert card.last_rep == -7
        assert card.next_rep == -8
        assert card.extra_data == "extra"
        assert card.scheduler_data == 1

    def test_update_tag(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact
        self.controller().edit_card_and_sisters(card, fact_data, card_type,
            new_tag_names=["default1"], correspondence=[])
        new_card = self.database().card(card._id, is_id_internal=True)
        tag_names = [tag.name for tag in new_card.tags]
        assert len(tag_names) == 1
        assert "default1" in tag_names
        assert self.database().con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 1

    def test_empty_argument(self):
        assert self.database().tags_from_cards_with_internal_ids([]) == []

    def test_clones(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact
        self.controller().clone_card_type(card_type, "my_1")

        new_card_type = self.card_type_with_id("1::my_1")
        self.controller().edit_card_and_sisters(card, fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        self.mnemosyne.finalise()
        self.restart()
        assert self.database().fact_count() == 1
        _card_id, _fact_id = list(self.database().cards_unseen())[0]
        fact = self.database().fact(_fact_id, is_id_internal=True)
        card_type = self.card_type_with_id("1::my_1")
        assert card_type.id == "1::my_1"
        assert card_type == card_type

    def test_plugin_and_clones(self):
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()

        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = self.card_type_with_id("4")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        assert self.database().fact_count() == 1

        fact = card.fact
        self.controller().clone_card_type(card_type, "my_4")

        new_card_type = self.card_type_with_id("4::my_4")
        self.controller().edit_card_and_sisters(card, fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        assert self.database().fact_count() == 1

        self.mnemosyne.finalise()

        self.restart()

        assert self.database().fact_count() == 1
        _card_id, _fact_id = list(self.database().cards_unseen())[0]
        fact = self.database().fact(_fact_id, is_id_internal=True)
        card_type = self.card_type_with_id("4")
        card_type = self.card_type_with_id("4::my_4")
        assert card_type.id == "4::my_4"
        assert card_type == card_type

        card = self.database().cards_from_fact(fact)[0]
        card.question()

    def off_new_database_overriding_existing_one(self):
        # causes permission problems under windows.
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])

        self.database().unload()
        self.database().new(self.config()["last_database"])

        assert self.database().fact_count() == 0

    def test_missing_plugin(self):
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()

        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = self.card_type_with_id("4")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact
        self.controller().clone_card_type(card_type, "my_4")

        new_card_type = self.card_type_with_id("4::my_4")
        self.controller().edit_card_and_sisters(card, fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])

        self.mnemosyne.finalise()
        self.restart()

        # Artificially remove plugin.
        self.database().unload()
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.deactivate()
                self.mnemosyne.component_manager.unregister(plugin)

        try:
            self.database().load(self.config()["last_database"])
            1/0
        except Exception as e:
            assert type(e) == RuntimeError


    def test_delete_fact(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]

        fact = card.fact
        self.controller().delete_facts_and_their_cards([fact])

        assert self.database().fact_count() == 0
        assert self.database().card_count() == 0
        assert len(self.database().tags()) == 1

    def infinity(self):
        return 1/0

    def test_corrupt_plugin(self):

        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()

        fact_data = {"loc": "location",
                     "blank": "blank",
                     "marked": "marked"}
        card_type = self.card_type_with_id("4")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact
        self.controller().clone_card_type(card_type, "my_4")

        new_card_type = self.card_type_with_id("4::my_4")
        self.controller().edit_card_and_sisters(card, fact_data,
               new_card_type, new_tag_names=["default2"], correspondence=[])
        self.mnemosyne.finalise()
        self.restart()
        self.database().unload()

        # Artificially mutilate plugin.
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.deactivate()
                plugin.activate = self.infinity
                break

        try:
            self.database().load(self.config()["last_database"])
            1/0
        except Exception as e:
            assert type(e) == RuntimeError

    def test_save_as(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        new_name = self.config()["last_database"] + ".bak"
        assert self.database().save(self.config()["last_database"] + ".bak") != -1
        assert self.config()["last_database"] == new_name
        assert new_name != expand_path(new_name, self.config().data_dir)

    def test_duplicates_for_fact(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)[0]
        fact = card.fact

        fact_data = {"f": "question_",
                     "b": "answer_"}
        card_type = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)
        assert len(self.database().duplicates_for_fact(fact, card_type)) == 0

        fact_data = {"f": "question1",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)
        assert len(self.database().duplicates_for_fact(fact, card_type)) == 0

        fact_data = {"f": "question",
                     "b": "answer1"}
        card_type = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)
        assert len(self.database().duplicates_for_fact(fact, card_type)) == 1

        fact_data = {"f": "question",
                     "b": "answer1"}
        card_type = self.card_type_with_id("2")
        self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["default"], check_for_duplicates=False)
        assert len(self.database().duplicates_for_fact(fact, card_type)) == 1

    def test_card_types_in_use(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        assert len(self.database().card_types_in_use()) == 1

        card_type = self.card_type_with_id("2")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        assert len(self.database().card_types_in_use()) == 2

    def test_vacuum(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
        for count in range(6):
            self.database().save()
            self.database().unload()
            self.database().load(self.config()["last_database"])

    def test_schedule_on_same_day(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_2 = self.card_type_with_id("2")
        card_1, card_2 = self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_3, card_4 = self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        self.review_controller().show_new_question()
        assert card_1 == self.review_controller().card
        assert self.database().sister_card_count_scheduled_between(card_1, 0, DAY) == 0
        self.review_controller().grade_answer(2)
        card_1 = self.database().card(card_1._id, is_id_internal=True)
        card_3.next_rep = card_1.next_rep
        card_3.grade = 2
        self.database().update_card(card_3)
        assert self.database().sister_card_count_scheduled_between(card_2, card_1.next_rep, card_1.next_rep+DAY) == 1
        assert self.database().sister_card_count_scheduled_between(card_3, card_1.next_rep, card_1.next_rep+DAY) == 0
        assert self.database().sister_card_count_scheduled_between(card_1, card_1.next_rep, card_1.next_rep+DAY) == 0

    def test_purge_backups(self):
        backup_dir = os.path.join(self.config().data_dir, "backups")
        for count in range(15):
            f = open(os.path.join(backup_dir, "default-%d.db" % count), "w")
        self.mnemosyne.finalise()
        backups = [f for f in os.listdir(backup_dir)]
        assert len(backups) == 10
        assert "default-0.db" not in backups
        self.restart()

    def test_link_inverse_cards(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card_type_2 = self.card_type_with_id("2")
        card_1 = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["tag_1"])[0]

        fact_data = {"f": "answer",
                     "b": "question"}
        card_2 = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["tag_1"])[0]

        self.database().save()
        self.database().link_inverse_cards()

        card_1 = self.database().card(card_1._id, is_id_internal=True)
        assert card_1.card_type == card_type_2
        assert card_1.fact_view == card_type_2.fact_views[0]
        card_1.fact['f'] = "Question"
        self.database().update_fact(card_1.fact)

        card_2 = self.database().card(card_2._id, is_id_internal=True)
        assert card_2.card_type == card_type_2
        assert card_2.fact_view == card_type_2.fact_views[1]
        assert "Question" in card_2.answer()

    def test_link_inverse_cards_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card_type_2 = self.card_type_with_id("2")
        card_1 = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["tag_1"])[0]

        fact_data = {"f": "answer",
                     "b": "question"}
        card_2 = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["tag_2"])[0]

        self.database().save()
        self.database().link_inverse_cards()

        card_1 = self.database().card(card_1._id, is_id_internal=True)
        assert card_1.card_type == card_type_1
        assert card_1.fact_view == card_type_1.fact_views[0]
        card_1.fact['f'] = "Question"
        self.database().update_fact(card_1.fact)

        card_2 = self.database().card(card_2._id, is_id_internal=True)
        assert card_2.card_type == card_type_1
        assert card_2.fact_view == card_type_1.fact_views[0]
        assert "Question" not in card_2.answer()

    def test_link_inverse_cards_3(self):
        fact_data = {"b": "question",
                     "f": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card_type_2 = self.card_type_with_id("2")
        card_1 = self.controller().create_new_cards(fact_data, card_type_2,
            grade=-1, tag_names=["tag_1"])[0]

        fact_data = {"f": "question",
                     "b": "answer"}
        card_2 = self.controller().create_new_cards(fact_data, card_type_2,
            grade=-1, tag_names=["tag_2"])[0]

        self.database().save()
        self.database().link_inverse_cards()

        card_1 = self.database().card(card_1._id, is_id_internal=True)
        card_1.fact['f'] = "Question"
        self.database().update_fact(card_1.fact)

        card_2 = self.database().card(card_2._id, is_id_internal=True)
        assert "Question" not in card_2.answer()

    def test_link_inverse_cards_4(self):
        fact_data = {"f": "sukuun",
                     "b": "zien"}
        card_type_1 = self.card_type_with_id("1")
        card_type_2 = self.card_type_with_id("2")
        card_1 = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["tag_1"])[0]

        fact_data = {"f": "no sukuun",
                     "b": "zien"}
        card_2 = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["tag_1"])[0]

        fact_data = {"f": "zien",
                     "b": "sukuun"}
        card_3 = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["tag_1"])[0]

        self.database().save()
        self.database().link_inverse_cards()

        card_1 = self.database().card(card_1._id, is_id_internal=True)
        assert card_1.card_type == card_type_2

        card_2 = self.database().card(card_2._id, is_id_internal=True)
        assert card_2.card_type == card_type_1

        card_3 = self.database().card(card_3._id, is_id_internal=True)
        assert card_3.card_type == card_type_2

    def test_link_inverse_cards_5(self):
        fact_data = {"f": "a",
                     "b": "a"}
        card_type_1 = self.card_type_with_id("1")
        card_type_2 = self.card_type_with_id("2")
        card_1 = self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["tag_1"])[0]

        self.database().save()
        self.database().link_inverse_cards()

        card_1 = self.database().card(card_1._id, is_id_internal=True)
        assert card_1.card_type == card_type_1

    def test_add_tag_to_card(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["default"])[0]
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 0

        tag = self.database().get_or_create_tag_with_name("new")
        self.database().add_tag_to_cards_with_internal_ids(tag, [card._id])

        new_card = self.database().card(card._id, is_id_internal=True)
        assert len(new_card.tags) == 2
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 1

        sql_res = self.database().con.execute(\
            "select event_type, object_id from log where _id=10").fetchone()
        assert sql_res[0] == EventTypes.EDITED_CARD
        assert sql_res[1] == card.id

        self.database().add_tag_to_cards_with_internal_ids(tag, [card._id])
        assert self.database().con.execute("select count() from tags_for_card").fetchone()[0] == 2
        assert len(new_card.tags) == 2
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 2

    def test_add_tag_to_untagged_card(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=[])[0]
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 0

        tag = self.database().get_or_create_tag_with_name("new")
        self.database().add_tag_to_cards_with_internal_ids(tag, [card._id])

        new_card = self.database().card(card._id, is_id_internal=True)
        assert len(new_card.tags) == 1
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 1

        self.database().add_tag_to_cards_with_internal_ids(tag, [card._id])
        assert self.database().con.execute("select count() from tags_for_card").fetchone()[0] == 1
        assert len(new_card.tags) == 1
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 2

    def test_remove_tag_from_card(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["a", "b"])[0]
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 0

        tag = self.database().get_or_create_tag_with_name("a")
        self.database().remove_tag_from_cards_with_internal_ids(tag, [card._id])

        new_card = self.database().card(card._id, is_id_internal=True)
        assert len(new_card.tags) == 1
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 1

        sql_res = self.database().con.execute(\
            "select event_type, object_id from log where _id=12").fetchone()
        assert sql_res[0] == EventTypes.EDITED_CARD
        assert sql_res[1] == card.id

    def test_remove_tag_from_card_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["a"])[0]
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 0

        tag = self.database().get_or_create_tag_with_name("a")
        assert self.database().con.execute("select count() from tags").fetchone()[0] == 2
        self.database().remove_tag_from_cards_with_internal_ids(tag, [card._id])
        assert self.database().con.execute("select count() from tags").fetchone()[0] == 1

        new_card = self.database().card(card._id, is_id_internal=True)
        assert len(new_card.tags) == 1
        assert list(new_card.tags)[0].name == "__UNTAGGED__"
        assert self.database().con.execute("select count() from tags_for_card where _tag_id=1 and _card_id=?",
            (card._id, )).fetchone()[0] == 1
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 1

        sql_contents = self.database().con.execute(\
            "select * from log").fetchall()

        sql_res = self.database().con.execute(\
            "select event_type, object_id from log where _id=10").fetchone()
        assert sql_res[0] == EventTypes.EDITED_CARD
        assert sql_res[1] == card.id

    def test_remove_tag_from_card_3(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=[])[0]
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 0

        tag = self.database().get_or_create_tag_with_name("a")
        self.database().remove_tag_from_cards_with_internal_ids(tag, [card._id])

        new_card = self.database().card(card._id, is_id_internal=True)
        assert len(new_card.tags) == 1
        assert list(new_card.tags)[0].name == "__UNTAGGED__"
        assert self.database().con.execute("select count() from tags_for_card where _tag_id=1 and _card_id=?",
            (card._id, )).fetchone()[0] == 1
        assert self.database().con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_CARD, )).fetchone()[0] == 1

        sql_contents = self.database().con.execute(\
            "select * from log").fetchall()

        sql_res = self.database().con.execute(\
            "select event_type, object_id from log where _id=10").fetchone()
        assert sql_res[0] == EventTypes.EDITED_CARD
        assert sql_res[1] == card.id

    def test_tags_for_cards(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["a", "b"])[0]
        card__id_1 = card._id
        fact_data = {"f": "question2",
                     "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["a"])[0]
        card__id_2 = card._id
        fact_data = {"f": "question3",
                     "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["c"])[0]
        card__id_3 = card._id

        for tag in self.database().tags_from_cards_with_internal_ids([card__id_1, card__id_2]):
            assert tag.name in ["a", "b"]

        for tag in self.database().tags_from_cards_with_internal_ids([card__id_2]):
            assert tag.name in ["a"]

        for tag in self.database().tags_from_cards_with_internal_ids([card__id_2, card__id_3]):
            assert tag.name in ["a", "c"]

    def test_tag_all_duplicates(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card_1 = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["a", "b"])[0]
        self.database().tag_all_duplicates()
        card_1 = self.database().card(card_1._id, is_id_internal=True)
        assert "DUPLICATE" not in card_1.tag_string()
        global answer
        answer = 1 # Add anyway
        card_2 = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["a", "b"])[0]
        fact_data = {"f": "question2",
                     "b": "answer"}
        card_3 = self.controller().create_new_cards(fact_data, card_type,
                                 grade=-1, tag_names=["a", "b"])[0]
        answer = None
        self.database().tag_all_duplicates()
        card_1 = self.database().card(card_1._id, is_id_internal=True)
        card_2 = self.database().card(card_2._id, is_id_internal=True)
        card_3 = self.database().card(card_3._id, is_id_internal=True)
        assert "DUPLICATE" in card_1.tag_string()
        assert "DUPLICATE" in card_2.tag_string()
        assert "DUPLICATE" not in card_3.tag_string()

    def test_is_accessible(self):
    #    from threading import Thread
    #    import time

    #    class MyThread(Thread):

    #        def __init__(self, mnemosyne):
    #            Thread.__init__(self)
    #            self.mnemosyne = mnemosyne

    #        def run(self):
    #            assert self.mnemosyne.database().is_accessible() == True
    #            self.mnemosyne.database().scheduled_count(0)
    #            time.sleep(0.2)
    #            self.mnemosyne.database().release_connection()

        assert self.database().is_accessible() == True
    #    self.database().release_connection()
    #    thread = MyThread(self)
    #    thread.start()
    #    time.sleep(0.1)
    #    assert self.database().is_accessible() == False
    #    time.sleep(0.3)

    def test_upgrade_2(self):
        shutil.copy(os.path.join("tests", "files", "non_unique_card_ids.db"),
                    os.path.join("dot_test", "tmp.db"))
        self.database().load(os.path.join("tmp.db"))
        card_1 = self.database().card(1, is_id_internal=True)
        card_2 = self.database().card(2, is_id_internal=True)
        assert card_1.id == "id"
        assert card_2.id == "id.1"

    def test_known_recognition(self):
        card_type = self.card_type_with_id("3")
        self.controller().clone_card_type(card_type, "my_3")
        card_type = self.card_type_with_id("3::my_3")
        fact_data = {"f": "yes_1",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        self.controller().create_new_cards(fact_data, card_type,
                                          grade=5, tag_names=["default"])

        fact_data = {"f": "no_1",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])

        card_type = self.card_type_with_id("3")
        self.controller().clone_card_type(card_type, "my_3_bis")
        card_type = self.card_type_with_id("3::my_3_bis")
        fact_data = {"f": "no_2",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])

        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "6":
                plugin.activate()

        card_type = self.card_type_with_id("6")
        fact_data = {"f": "yes_2",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        self.controller().create_new_cards(fact_data, card_type,
                                          grade=5, tag_names=["default"])

        fact_data = {"f": "no_3",
                     "p_1": "pronunciation",
                     "m_1": "translation"}
        self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])

        assert self.database().\
           known_recognition_questions_count_from_card_types_ids(["3::my_3"]) == 1
        assert self.database().\
           known_recognition_questions_count_from_card_types_ids(["3::my_3_bis"]) == 0
        assert self.database().\
           known_recognition_questions_count_from_card_types_ids(["6"]) == 1
        assert self.database().\
           known_recognition_questions_count_from_card_types_ids(\
               ["6", "3::my_3", "3::my_3_bis"]) == 2

        assert set((self.database().\
           known_recognition_questions_from_card_types_ids(\
               ["6", "3::my_3", "3::my_3_bis"]))) == set(["yes_1", "yes_2"])

    def _start_and_end_timestamp(self):
        timestamp = time.time() - 0 - self.config()["day_starts_at"] * HOUR
        date_only = datetime.date.fromtimestamp(timestamp)  # Local date.
        start_of_day = int(time.mktime(date_only.timetuple()))
        start_of_day += self.config()["day_starts_at"] * HOUR

        return start_of_day, start_of_day + DAY

    def test_has_already_warned(self):
        now = int(time.time())

        start_of_day, end_of_day = self._start_and_end_timestamp()

        assert self.database().has_already_warned_today(start_of_day, start_of_day + DAY) == False
        self.database().log_warn_about_too_many_cards(now)
        assert self.database().has_already_warned_today(start_of_day, start_of_day + DAY) == True

    def test_fact_ids_forgotten_and_learned_today(self):
        start_of_day, end_of_day = self._start_and_end_timestamp()

        assert list(self.database().fact_ids_forgotten_and_learned_today(start_of_day, end_of_day)) == []

        # create 5 cards with id 1..5
        cards = self._create_n_test_cards(5)

        # forgot 5 cards (only log)
        last_timestamp = self._generate_n_forgotten_card_logs(5, cards)

        # learn 3 forgotten cards (only log)
        self._learn_n_forgotten_cards_logs(3, last_timestamp, cards)

        forgotten_and_learned = self.database().fact_ids_forgotten_and_learned_today(start_of_day, end_of_day)

        assert len([x for x in forgotten_and_learned]) == 3

    def test_fact_ids_newly_learned_today(self):
        start_of_day, end_of_day = self._start_and_end_timestamp()

        cards = self._create_n_test_cards(15)

        new_fact_ids = [_fact_ids for _fact_ids in self.database().fact_ids_newly_learned_today(start_of_day, end_of_day)]
        assert len(new_fact_ids) == 0

        self._learn_n_new_cards_logs(7, start_of_day, cards)

        new_fact_ids = [_fact_ids for _fact_ids in self.database().fact_ids_newly_learned_today(start_of_day, end_of_day)]
        assert len(new_fact_ids) == 7

    def _create_n_test_cards(self, n):
        """a helper function to generate n cards

        """
        cards = []
        card_type = self.card_type_with_id("1")
        for i in range(n):
            fact_data = {"f": "foreign word %d" % i,
                         "p_1": "pronunciation %d" % i,
                         "m_1": "translation %d" % i}
            c = self.controller().create_new_cards(fact_data, card_type,
                                                   grade=-1, tag_names=["default"])
            cards.append(c[0])
        return cards

    def _generate_n_forgotten_card_logs(self, n, cards):
        """a helper function to generate n forgotten cards log entry

        """
        start_of_day, end_of_day = self._start_and_end_timestamp()

        fake_timestamp = start_of_day + 300
        for x in range(n):
            self.database().con.execute(
                """insert into log(event_type, timestamp, object_id,
                grade, ret_reps, lapses)
                values(?,?,?,?,?,?)""",
                (EventTypes.REPETITION, int(fake_timestamp), cards[x].id, 1, 1, 1))
            fake_timestamp += 300

        return fake_timestamp

    def _learn_n_forgotten_cards_logs(self, n, start_timestamp, cards):
        """a helper function to re-learn n forgotten cards log entry

        """

        fake_timestamp = start_timestamp + 300
        for x in range(n):
            self.database().con.execute(
                """insert into log(event_type, timestamp, object_id,
                grade, ret_reps, lapses)
                values(?,?,?,?,?,?)""",
                (EventTypes.REPETITION, int(fake_timestamp), cards[x].id, 2, 1, 1))
            fake_timestamp += 300

    def _learn_n_new_cards_logs(self, n, start_timestamp, cards):
        """a helper function to learn n new cards log entry

        """

        fake_timestamp = start_timestamp + 300
        for x in range(n):
            self.database().con.execute(
                """insert into log(event_type, timestamp, object_id,
                grade, ret_reps, lapses)
                values(?,?,?,?,?,?)""",
                (EventTypes.REPETITION, int(fake_timestamp), cards[x].id, 2, 0, 0))
            fake_timestamp += 300
