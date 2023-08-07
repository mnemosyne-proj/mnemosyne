#
# test_activate_cards.py <Peter.Bienstman@UGent.be>
#

from pytest import raises
from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.criterion import Criterion
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion

class TestActivateCards(MnemosyneTest):

    def test_compare_criteria(self):
        c1 = DefaultCriterion(self.mnemosyne.component_manager)
        c1.deactivated_card_type_fact_view_ids = set()
        c1._tag_ids_active = set([self.database().get_or_create_tag_with_name("default")._id])
        c1._tag_ids_forbidden = set()

        c2 = DefaultCriterion(self.mnemosyne.component_manager)
        c2.deactivated_card_type_fact_view_ids = set()
        c2._tag_ids_active = set([self.database().get_or_create_tag_with_name("default")._id])
        c2._tag_ids_forbidden = set()

        c3 = DefaultCriterion(self.mnemosyne.component_manager)
        c3.deactivated_card_type_fact_view_ids = set()
        c3._tag_ids_active = set([self.database().get_or_create_tag_with_name("default1")._id])
        c3._tag_ids_forbidden = set()

        assert c1 == c2
        assert c1 != c3
        assert c1 != 1

    def test_activate_cards_1(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
                                              grade=-1, tag_names=["default"])
        assert self.database().active_count() == 1

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_2 = self.card_type_with_id("2")
        self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default"])
        assert self.database().active_count() == 3

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("default")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 3

        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_2.id, card_type_2.fact_views[0].id)])
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("default")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 2

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("default2")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

        fact_data = {"f": "question2",
                     "b": "answer2"}
        self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default2"])
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("default2")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 2

        fact_data = {"f": "question3",
                     "b": "answer3"}
        self.controller().create_new_cards(fact_data, card_type_2,
                                              grade=-1, tag_names=["default3",
                                                                  "default4"])
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("default3")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 2

        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_2.id, card_type_2.fact_views[0].id)])
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("default3")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 1

        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_2.id, card_type_2.fact_views[0].id),
                 (card_type_2.id, card_type_2.fact_views[1].id)])
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("default3")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

    def test_activate_cards_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["active", "forbidden"])
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("active")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("active")._id])
        c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

    def test_activate_cards_3(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["tag1"])[0]
        self.review_controller().show_new_question()

        assert self.review_controller().card == card
        assert self.review_controller().counters() == (0, 1, 1)

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_type_2 = self.card_type_with_id("2")
        cards = self.controller().create_new_cards(fact_data, card_type_2,
           grade=-1, tag_names=["tag2"])

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("tag2")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().reload_counters()

        assert self.review_controller().card != card
        assert self.review_controller().counters() == (0, 2, 2)

    def test_activate_cards_4(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["tag"])[0]
        self.review_controller().show_new_question()

        assert self.review_controller().card == card
        assert self.review_controller().counters() == (0, 1, 1)

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("tag2")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().reload_counters()

        assert self.review_controller().card is None
        assert self.review_controller().counters() == (0, 0, 0)

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("tag")._id])
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().reload_counters()

        assert self.review_controller().card == card
        assert self.review_controller().counters() == (0, 1, 1)

    def test_activate_cards_new(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["forbidden"])
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["forbidden"])
        assert self.database().active_count() == 0

    def test_activate_cards_new_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_1.id, card_type_1.fact_views[0].id)])
        c._tag_ids_active = set()
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])
        assert self.database().active_count() == 0

    def test_activate_cards_edit(self):
        fact_data = {"f": "question3",
                     "b": "answer3"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["forbidden"])[0]
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

        card_type_2 = self.card_type_with_id("2")
        self.controller().edit_card_and_sisters(card, card.fact.data,
               card_type_2, new_tag_names=["allowed"], correspondence=[])
        assert self.database().active_count() == 2

        c = list(self.database().criteria())[0]
        assert len(c._tag_ids_forbidden) == 0
        assert len(c._tag_ids_active) == 1

    def test_activate_cards_bulk_edit(self):
        fact_data = {"f": "question3",
                     "b": "answer3"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["allowed"])[0]
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("allowed")._id])
        c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 1

        self.database().add_tag_to_cards_with_internal_ids(\
            self.database().get_or_create_tag_with_name("forbidden"), [card._id])
        
        assert self.database().active_count() == 0

    def test_activate_cards_bulk_edit_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["forbidden"])[0]

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["forbidden"])[0]
        assert self.database().active_count() == 2

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("__UNTAGGED__")._id])
        c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

        self.database().remove_tag_from_cards_with_internal_ids(\
            self.database().get_or_create_tag_with_name("forbidden"), [card._id])

        assert self.database().active_count() == 1
        
    def test_card_type(self):
        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin
        for plugin in self.plugins():
            if isinstance(plugin, ClozePlugin):
                cloze_plugin = plugin
                plugin.activate()
                break

        fact_data = {"text": "[foo]"}
        card_type_1 = self.card_type_with_id("5")
        card = self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])[0]
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_1.id, card_type_1.fact_views[0].id)])
        c._tag_ids_active = set()
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

        self.controller().delete_facts_and_their_cards([card.fact])
        plugin.deactivate()
        c = self.database().current_criterion()
        assert len(c.deactivated_card_type_fact_view_ids) == 0

    def test_cached_scheduler_count(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["tag"])
        assert self.database().active_count() == 1
        self.review_controller().show_new_question()
        assert self.review_controller().active_count == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set()
        c._tag_ids_forbidden = set()
        self.database().set_current_criterion(c)
        self.review_controller().reset_but_try_to_keep_current_card()
        assert self.database().active_count() == 0
        assert self.review_controller().active_count == 0

    def test_activate_cards_5(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["b"])

        fact_data = {"f": "question2",
                     "b": "answer2"}
        self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["a"])
        assert self.database().active_count() == 2

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("a")._id,
                                 self.database().get_or_create_tag_with_name("b")._id])
        c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("b")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 1

    def test_activate_cards_6(self):
        with raises(AssertionError):
            fact_data = {"f": "question",
                         "b": "answer"}
            card_type_1 = self.card_type_with_id("1")
            self.controller().create_new_cards(fact_data, card_type_1,
               grade=-1, tag_names=["a"])

            fact_data = {"f": "question2",
                         "b": "answer2"}
            self.controller().create_new_cards(fact_data, card_type_1,
                grade=-1, tag_names=["b"])
            assert self.database().active_count() == 2

            c = DefaultCriterion(self.mnemosyne.component_manager)
            c.deactivated_card_type_fact_view_ids = set()
            c._tag_ids_active = set([])
            c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("b")._id])
            self.database().set_current_criterion(c)
            assert self.database().active_count() == 1

    def test_empty_criterion(self):
        c = Criterion(self.mnemosyne.component_manager)
        assert c.is_empty() == False

        tag_id = self.database().get_or_create_tag_with_name("a")._id

        c = DefaultCriterion(self.mnemosyne.component_manager)
        for card_type in self.card_types():
            for fact_view in card_type.fact_views:
                c.deactivated_card_type_fact_view_ids.add((card_type.id, fact_view.id))
        c._tag_ids_active = set([])
        c._tag_ids_forbidden = set()
        assert c.is_empty() == True

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([])
        c._tag_ids_forbidden = set()
        assert c.is_empty() == True

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set(["__UNTAGGED__"])
        c._tag_ids_forbidden = set([tag_id])
        assert c.is_empty() == False

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set(["__UNTAGGED__"])
        c._tag_ids_forbidden = set([tag_id, "__UNTAGGED__"])
        assert c.is_empty() == True

    def test_inactive_parent(self):

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["dummy"])

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card_type_1 = self.card_type_with_id("1")
        self.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["a"])

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("dummy")._id])
        c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("a")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 1

        fact_data = {"f": "question3",
                     "b": "answer3"}
        self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["a::b"])

        assert self.database().active_count() == 1
        fact_data = {"f": "question4",
                     "b": "answer4"}
        self.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["dummy::b"])
        assert self.database().active_count() == 2
