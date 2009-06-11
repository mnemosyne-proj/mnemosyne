#
# test_card_type.py <Peter.Bienstman@UGent.be>
#

from mnemosyne_test import MnemosyneTest

class TestCardType(MnemosyneTest):

    def test_card_types(self):
        card_type = self.card_type_by_id("1")
        assert card_type.key_with_name("Question") == "q"
        assert card_type.required_fields() == set("q")
        assert card_type.validate_data("foo") == True
