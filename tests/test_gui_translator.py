#
# test_gui_translator.py <Peter.Bienstman@UGent.be>
#


from mnemosyne_test import MnemosyneTest
from mnemosyne.libmnemosyne.gui_translator import GuiTranslator
from mnemosyne.libmnemosyne.gui_translators.no_gui_translator import NoGuiTranslator
from mnemosyne.libmnemosyne.gui_translator import iso6931_code_for_language_name
from mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator import GetTextGuiTranslator

class TestGuiTranslator(MnemosyneTest):

    def test_gui_translator_2(self):
        self.mnemosyne.gui_translator()
        t = NoGuiTranslator(None)
        assert t("foo") == "foo"

    def test_gui_translator_3(self):
        card_type = self.card_type_with_id("1")
        assert card_type._()

    def test_fallback(self):
        from mnemosyne.libmnemosyne.gui_translator import _
        assert _("foo") == "foo"

    def test_gui_translation(self):
        from mnemosyne.libmnemosyne.gui_translator import _
        self.config()["ui_language"] = "de"
        self.mnemosyne.component_manager.current(
                "gui_translator").set_language("de")
        assert _("This is a test.") == "Dies ist ein Test."

    def test_1(self):
        t = GuiTranslator(self.mnemosyne.component_manager)
        assert t.supported_languages() == []
        assert iso6931_code_for_language_name("Zulu") == "zu"

        t = GetTextGuiTranslator(self.mnemosyne.component_manager)
        assert t.supported_languages() != []


