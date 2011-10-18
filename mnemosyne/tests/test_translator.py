#
# test_translator.py <Peter.Bienstman@UGent.be>
#


from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.translator import Translator
from mnemosyne.libmnemosyne.translators.no_translator import NoTranslator


class TestTranslator(MnemosyneTest):
    
    def test_translator_2(self):
        t = NoTranslator(None)
        assert t("foo") == "foo"
    
    def test_translator_3(self):
        card_type = self.card_type_with_id("1")
        assert card_type._()
    
    def test_fallback(self):
        from mnemosyne.libmnemosyne.translator import _
        assert _("foo") == "foo"

    def test_translation(self):
        from mnemosyne.libmnemosyne.translator import _
        self.config()["ui_language"] = "de"
        self.mnemosyne.component_manager.current(
                "translator").set_language("de")
        assert _("This is a test.") == "Dies ist ein Test."
