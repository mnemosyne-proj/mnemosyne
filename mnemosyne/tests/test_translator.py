#
# test_translator.py <Peter.Bienstman@UGent.be>
#

from nose.tools import raises

from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.translator import Translator, NoTranslation


class TestTranslator(object):
    
    @raises(NotImplementedError)
    def test_translator_1(self):
        t = Translator(None)
        t("foo")
              
    def test_translator_2(self):
        t = NoTranslation(None)
        assert t("foo") == "foo"

        
class TestTranslator2(MnemosyneTest):
    def test_translator_3(self):
        card_type = self.card_type_by_id("1")
        assert card_type._()
        
