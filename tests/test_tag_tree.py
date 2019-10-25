#
# test_tag_tree.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion


class TestTagTree(MnemosyneTest):

    def test_1(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=[])[0]
        self.controller().save_file()
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert len(list(self.tree.keys())) == 2
        assert self.tree['__ALL__'] == ['__UNTAGGED__']

    def test_2(self):
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag_1"])[0]
        self.controller().save_file()
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert len(list(self.tree.keys())) == 3
        assert self.tree['__ALL__'] == ['tag_1', '__UNTAGGED__']

    def test_3(self):
        fact_data = {"f": "question", "b": "answer"}
        card_type = self.card_type_with_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]
        fact_data = {"f": "question2", "b": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"f": "question3",  "b": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"f": "question5",  "b": "answer5"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["b::c::d"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert self.tree.card_count_for_node["b"] == 1
        assert self.tree.card_count_for_node["b::c"] == 1
        assert self.tree.card_count_for_node["b::c::d"] == 1
        assert self.tree.nodes() == \
               ["a", "a::Untagged", "a::b", "a::c", "b", "b::c", "b::c::d",
                "Z", "__UNTAGGED__"]

    def test_4(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]
        fact_data = {"f": "question2", "b": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"f": "question3",  "b": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"f": "question5",  "b": "answer5"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["b::c::d"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert self.tree.card_count_for_node["b"] == 1
        assert self.tree.card_count_for_node["b::c"] == 1
        assert self.tree.card_count_for_node["b::c::d"] == 1

        self.tree.rename_node("Z", "Z::Z")
        self.tree.rename_node("b::c", "b::cc")
        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["Z::Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert self.tree.card_count_for_node["b"] == 1
        assert self.tree.card_count_for_node["b::cc"] == 1
        assert self.tree.card_count_for_node["b::cc::d"] == 1

    def test_5(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]
        fact_data = {"f": "question2", "b": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"f": "question3",  "b": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"f": "question5",  "b": "answer5"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["b::c::d"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert self.tree.card_count_for_node["b"] == 1
        assert self.tree.card_count_for_node["b::c"] == 1
        assert self.tree.card_count_for_node["b::c::d"] == 1

        self.tree.rename_node("b::c", "b")
        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert self.tree.card_count_for_node["b"] == 1
        assert self.tree.card_count_for_node["b::d"] == 1

    def test_rename_to_existing_tag(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag1"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag2"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert len(self.database().tags()) == 3
        self.tree.rename_node("tag1", "tag2")
        assert self.tree.card_count_for_node["tag2"] == 2
        assert len(self.database().tags()) == 2

    def test_rename_to_existing_tag_2(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Xx::vb::test", "Xx::aa::vb::test"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert len(self.database().tags()) == 3
        self.tree.rename_node("Xx::aa::vb::test", "Xx::vb::test")
        assert self.tree.card_count_for_node["Xx::vb::test"] == 1
        assert "Xx::aa::vb::test" not in self.tree.card_count_for_node
        assert "," not in  self.database().con.execute(\
            "select tags from cards where _id=?", (card._id,)).fetchone()[0]
        assert self.database().con.execute(\
            "select count() from tags_for_card").fetchone()[0] == 1
        assert len(self.database().tags()) == 2

    def test_rename_to_empty(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag1"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag2"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        self.tree.rename_node("tag1", "")
        assert self.tree.card_count_for_node["__UNTAGGED__"] == 1
        assert len(self.database().tags()) == 2

    def test_rename_to_empty_2(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["A::tag1"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        self.tree.rename_node("A", "")
        assert self.tree.card_count_for_node["tag1"] == 1
        assert len(self.database().tags()) == 2

    def test_rename_to_empty_3(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["A::tag1"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["A"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        self.tree.rename_node("A", "")
        assert self.tree.card_count_for_node["__UNTAGGED__"] == 1
        assert self.tree.card_count_for_node["tag1"] == 1
        assert len(self.database().tags()) == 2

    def test_rename_to_forbidden(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["A::tag1"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["A"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        self.tree.rename_node("A", "__UNTAGGED__")
        assert "__UNTAGGED__" in self.tree.card_count_for_node

    def test_delete(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]
        fact_data = {"f": "question2", "b": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"f": "question3",  "b": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"f": "question5",  "b": "answer5"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["b::c::d"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert self.tree.card_count_for_node["b"] == 1
        assert self.tree.card_count_for_node["b::c"] == 1
        assert self.tree.card_count_for_node["b::c::d"] == 1

        self.tree.delete_subtree("b::c")

        card = self.database().card(card._id, is_id_internal=True)
        assert card.tag_string() == ""
        self.database().con.execute("select tags from cards where _id=?",
            (card._id, )).fetchone()[0] == ""

        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert self.tree.card_count_for_node["__UNTAGGED__"] == 1
        assert "b" not in self.tree.card_count_for_node
        assert "b::c" not in self.tree.card_count_for_node
        assert "b::c::d" not in self.tree.card_count_for_node

    def test_delete_2(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]
        fact_data = {"f": "question2", "b": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"f": "question3",  "b": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"f": "question5",  "b": "answer5"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["b::c::d", "b"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)

        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert self.tree.card_count_for_node["b"] == 1
        assert self.tree.card_count_for_node["b::c"] == 1
        assert self.tree.card_count_for_node["b::c::d"] == 1

        self.tree.delete_subtree("b::c")
        card = self.database().card(card._id, is_id_internal=True)
        assert card.tag_string() == ""
        self.database().con.execute("select tags from cards where _id=?",
            (card._id, )).fetchone()[0] == "b"

        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert "b" not in self.tree.card_count_for_node
        assert "__UNTAGGED__" in self.tree.card_count_for_node
        assert "b::c" not in self.tree.card_count_for_node
        assert "b::c::d" not in self.tree.card_count_for_node

    def test_count_1(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["b"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["b", "b"])[0]

        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)

        assert self.tree.card_count_for_node["__ALL__"] == 2

    def test_count_2(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question4",  "b": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["X::a"])[0]
        fact_data = {"f": "question", "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["X::a", "X::b"])[0]

        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)

        assert self.tree.card_count_for_node["__ALL__"] == 2
        assert self.tree.card_count_for_node["X"] == 2

    def test_delete_forbidden(self):
        card_type = self.card_type_with_id("1")
        fact_data = {"f": "question",  "b": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["forbidden"])[0]
        assert self.database().active_count() == 1

        c = DefaultCriterion(self.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.database().get_or_create_tag_with_name("active")._id, 1])
        c._tag_ids_forbidden = set([self.database().get_or_create_tag_with_name("forbidden")._id])
        self.database().set_current_criterion(c)
        assert self.database().active_count() == 0

        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        self.tree.delete_subtree("forbidden")
        assert self.database().active_count() == 1
