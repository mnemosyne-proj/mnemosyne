#
# test_plugin.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises

import os

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.component_manager import card_types
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import database, plugins
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack

class Widget(MainWidget):

    def information_box(self, s1):
        raise NotImplementedError

class MyCardType(FrontToBack):
    id = "666"

class MyPlugin(Plugin):
    name = "myplugin"
    description = "MyPlugin"
    components = [MyCardType]
    
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
        p = Plugin()
        
    @raises(NotImplementedError)
    def test_2(self):
             
        p = MyPlugin()

        old_length = len(card_types())
        p.activate()
        assert len(card_types()) == old_length + 1
        p.deactivate()              
        assert len(card_types()) == old_length

        p.activate()

        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("666")
        ui_controller_main().create_new_cards(fact_data, card_type,
                                              grade=0, cat_names=["default"])
        p.deactivate() # Pops up an information box that this is not possible.

    @raises(NotImplementedError)
    def test_3(self):
        p = MyPlugin()
        p.activation_message = "Hi"
        p.activate() # Should print activation message.
       
    def test_4(self):
        p = MyPlugin()

        old_length = len(card_types())
        p.activate()
        assert len(card_types()) == old_length + 1
        p.deactivate()              
        assert len(card_types()) == old_length

        p.activate()

        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = card_type_by_id("666")
        card = ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])[0]
        fact = card.fact
        database().delete_fact_and_related_data(fact)
        
        p.deactivate() # Should work without problems.
