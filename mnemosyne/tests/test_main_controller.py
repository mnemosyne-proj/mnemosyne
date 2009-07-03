#
# test_main_controller.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest


class TestMainController(MnemosyneTest):

    def test_coverage(self):
        self.ui_controller_main().heartbeat()
        self.ui_controller_main().add_cards()
        card_type = self.card_type_by_id("2")
        fact_data = {"q": "q", "a": "a"}
        card_1, card_2 = self.ui_controller_main().create_new_cards(fact_data,
          card_type, grade=-1, tag_names=["default"])
        self.ui_controller_review().new_question()        
        self.ui_controller_main().edit_current_card()        
        self.ui_controller_main().file_new()
        self.ui_controller_main().file_open()
        self.ui_controller_main().file_save_as()
        self.ui_controller_main().card_appearance()        
        self.ui_controller_main().activate_plugins()  
        self.ui_controller_main().manage_card_types()        
        self.ui_controller_main().browse_cards()
        self.ui_controller_main().configure()
        self.ui_controller_main().show_statistics()
