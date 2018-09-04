#
# google_translator.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.translator import Translator


class GoogleTranslator(Translator):

    used_for = "ar"  # TMP
    popup_menu_text = "Insert Google translation..."

    def translate(self, text):
        # TMP
        return text.upper()
