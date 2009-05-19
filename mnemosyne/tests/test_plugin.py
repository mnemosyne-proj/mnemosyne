#
# test_plugin.py <Peter.Bienstman@UGent.be>
#

import os
from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class Widget(MainWidget):

    def information_box(self, s1):
        raise NotImplementedError

class TestPlugin(MnemosyneTest):

    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_plugin", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"))
        
    @raises(AssertionError)
    def test_1(self):
        from mnemosyne.libmnemosyne.plugin import Plugin
        p = Plugin(self.mnemosyne.component_manager)
        
    @raises(NotImplementedError)
    def test_2(self):

        from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
        from mnemosyne.libmnemosyne.plugin import Plugin
        
        class MyCardType(FrontToBack):
            id = "666"

        class MyPlugin(Plugin):
            name = "myplugin"
            description = "MyPlugin"
            components = [MyCardType]
    
        p = MyPlugin(self.mnemosyne.component_manager)

        old_length = len(self.card_types())
        p.activate()
        assert len(self.card_types()) == old_length + 1
        p.deactivate()              
        assert len(self.card_types()) == old_length

        p.activate()

        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("666")
        self.ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        p.deactivate() # Pops up an information box that this is not possible.
       
    def test_3(self):

        from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
        from mnemosyne.libmnemosyne.plugin import Plugin

        class MyCardType(FrontToBack):
            id = "666"

        class MyPlugin(Plugin):
            name = "myplugin"
            description = "MyPlugin"
            components = [MyCardType]
            
        p = MyPlugin(self.mnemosyne.component_manager)

        old_length = len(self.card_types())
        p.activate()
        assert len(self.card_types()) == old_length + 1
        p.deactivate()              
        assert len(self.card_types()) == old_length

        p.activate()

        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.card_type_by_id("666")
        card = self.ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        fact = card.fact
        self.database().delete_fact_and_related_data(fact)
        
        p.deactivate() # Should work without problems.
