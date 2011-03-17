#
# test_plugin.py <Peter.Bienstman@UGent.be>
#

import os
from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

class Widget(MainWidget):

    def show_information(self, s1):
        raise NotImplementedError

class TestPlugin(MnemosyneTest):

    def setup(self):
        os.system("rm -fr dot_test")
        
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(\
            ("test_plugin", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne_test", "TestReviewWidget"))
        self.mnemosyne.initialise(os.path.abspath("dot_test"),  automatic_upgrades=False)
        self.review_controller().reset()
        
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

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_by_id("666")
        self.controller().create_new_cards(fact_data, card_type,
                                              grade=-1, tag_names=["default"])
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

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.card_type_by_id("666")
        card = self.controller().create_new_cards(fact_data, card_type,
                                          grade=-1, tag_names=["default"])[0]
        fact = card.fact
        self.controller().delete_facts_and_their_cards([fact])
        
        p.deactivate() # Should work without problems.

    def test_4(self):
   
        from mnemosyne.libmnemosyne.plugin import Plugin
        from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
        from mnemosyne.pyqt_ui.card_type_wdgt_generic import GenericCardTypeWdgt

        class RedGenericCardTypeWdgt(GenericCardTypeWdgt):

            used_for = FrontToBack

            def __init__(self, parent, component_manager):
                GenericCardTypeWdgt.__init__(self, component_manager,
                                             parent, FrontToBack())

        class RedPlugin(Plugin):
            name = "Red"
            description = "Red widget for front-to-back cards"
            components = [RedGenericCardTypeWdgt]
            
        p = RedPlugin(self.mnemosyne.component_manager)
        p.activate()
        assert self.mnemosyne.component_manager.current\
                    ("generic_card_type_widget", used_for=FrontToBack) != None
        p.deactivate()  
        assert self.mnemosyne.component_manager.current\
                    ("generic_card_type_widget", used_for=FrontToBack) == None

    def test_5(self):   
        for plugin in self.plugins():
            component = plugin.components[0]
            if component.component_type == "card_type" and component.id == "4":
                plugin.activate()
                plugin.activate()

    @raises(NotImplementedError)
    def test_6(self):
        from mnemosyne.libmnemosyne.hook import Hook
        Hook(self.mnemosyne.component_manager).run()
