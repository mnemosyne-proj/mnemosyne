#
# test_tag_tree.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest

  
class TestTagTree(MnemosyneTest):

    def test_1(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=[])[0]
        self.controller().file_save()
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        print self.tree.keys()
        assert len(self.tree.keys()) == 2
        assert self.tree['__ALL__'] == [u'__UNTAGGED__']
        
    def test_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag_1"])[0]
        self.controller().file_save()
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert len(self.tree.keys()) == 2
        assert self.tree['__ALL__'] == [u'tag_1']

    def test_3(self):
        fact_data = {"q": "question", "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]         
        fact_data = {"q": "question2", "a": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"q": "question3",  "a": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"q": "question5",  "a": "answer5"}
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
        
    def test_4(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"q": "question", "a": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]         
        fact_data = {"q": "question2", "a": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"q": "question3",  "a": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"q": "question5",  "a": "answer5"}
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
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"q": "question", "a": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]         
        fact_data = {"q": "question2", "a": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"q": "question3",  "a": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"q": "question5",  "a": "answer5"}
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
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag1"])[0]
        fact_data = {"q": "question", "a": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag2"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        self.tree.rename_node("tag1", "tag2")
        assert self.tree.card_count_for_node["tag2"] == 2
        assert len(self.database().tags()) == 1
        
    def test_rename_to_empty(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag1"])[0]
        fact_data = {"q": "question", "a": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["tag2"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        self.tree.rename_node("tag1", "")
        assert self.tree.card_count_for_node["__UNTAGGED__"] == 1
        assert len(self.database().tags()) == 2
        
    def test_rename_to_empty_2(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["A::tag1"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        self.tree.rename_node("A", "")
        assert "__UNTAGGED__" not in self.tree.card_count_for_node
        assert self.tree.card_count_for_node["tag1"] == 1
        assert len(self.database().tags()) == 1

    def test_rename_to_empty_3(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["A::tag1"])[0]
        fact_data = {"q": "question", "a": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["A"])[0]
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        self.tree.rename_node("A", "")
        assert self.tree.card_count_for_node["__UNTAGGED__"] == 1
        assert self.tree.card_count_for_node["tag1"] == 1
        assert len(self.database().tags()) == 2

    def test_delete(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"q": "question", "a": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]         
        fact_data = {"q": "question2", "a": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"q": "question3",  "a": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"q": "question5",  "a": "answer5"}
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

        card = self.database().card(card._id, id_is_internal=True)
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
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::b"])[0]
        fact_data = {"q": "question", "a": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]         
        fact_data = {"q": "question2", "a": "answer2"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["Z"])[0]
        fact_data = {"q": "question3",  "a": "answer3"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a::c"])[0]
        fact_data = {"q": "question5",  "a": "answer5"}
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
        print self.tree.card_count_for_node
        card = self.database().card(card._id, id_is_internal=True)
        assert card.tag_string() == "b"
        self.database().con.execute("select tags from cards where _id=?",
            (card._id, )).fetchone()[0] == "b"
        
        assert self.tree.card_count_for_node["__ALL__"] == 5
        assert self.tree.card_count_for_node["a"] == 3
        assert self.tree.card_count_for_node["Z"] == 1
        assert self.tree.card_count_for_node["a::b"] == 1
        assert self.tree.card_count_for_node["a::c"] == 1
        assert self.tree.card_count_for_node["b"] == 1
        assert "__UNTAGGED__" not in self.tree.card_count_for_node == 1
        assert "b::c" not in self.tree.card_count_for_node
        assert "b::c::d" not in self.tree.card_count_for_node

    def test_count_1(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]
        fact_data = {"q": "question", "a": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a", "b"])[0]
        
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        
        assert self.tree.card_count_for_node["__ALL__"] == 2
        
    def test_count_2(self):
        card_type = self.card_type_by_id("1")
        fact_data = {"q": "question4",  "a": "answer4"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["X::a"])[0]
        fact_data = {"q": "question", "a": "answer"}
        card = self.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["X::a", "X::b"])[0]
        
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        
        assert self.tree.card_count_for_node["__ALL__"] == 2
        assert self.tree.card_count_for_node["X"] == 2 
