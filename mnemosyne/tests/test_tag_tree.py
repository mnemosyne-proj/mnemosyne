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
        assert len(self.tree.tree.keys()) == 1
        assert self.tree.tree['__ALL__'] == [u'__UNTAGGED__']
        
    def test_2(self):
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("1")
        card = self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["tag_1"])[0]
        self.controller().file_save()
        from mnemosyne.libmnemosyne.tag_tree import TagTree
        self.tree = TagTree(self.mnemosyne.component_manager)
        assert len(self.tree.tree.keys()) == 1
        assert self.tree.tree['__ALL__'] == [u'tag_1']
