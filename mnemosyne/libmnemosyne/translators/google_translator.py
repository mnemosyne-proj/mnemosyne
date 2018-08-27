#
# google_translator.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.translator import Translator


class GoogleTranslator(Translator):

    """Generic translation service for words and sentences. Not to be confused
    the GuiTranslator, which is for translating the user interface.

    """

    component_type = "translator"
    used_for = "ar"  # TMP
    popup_menu_text = "Insert Google translation..."

    def translate(self, text):
        # TMP
        return text.upper()
