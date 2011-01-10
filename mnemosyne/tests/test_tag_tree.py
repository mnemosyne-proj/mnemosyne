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
