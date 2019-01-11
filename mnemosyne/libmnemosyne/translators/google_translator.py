#
# google_translator.py <Peter.Bienstman@UGent.be>
#

from googletrans import Translator as gTranslator

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.translator import Translator


class GoogleTranslator(Translator):

    used_for = "ar", "en", "fr"  # TMP
    popup_menu_text = "Insert Google translation..."

    def translate(self, card_type, foreign_text, dest_language_id):
        src_language_id = self.config().card_type_property(\
            "language_id", card_type)
        return gTranslator().translate(foreign_text, src_language_id,
                dest_language_id).text
