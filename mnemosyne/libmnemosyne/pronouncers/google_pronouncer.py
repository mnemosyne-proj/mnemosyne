#
# google_pronouncer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.pronouncer import Pronouncer


class GooglePronouncer(Pronouncer):

    used_for = "ar"  # TMP
    popup_menu_text = "Insert Google text-to-speech..."

    def pronounce(self, text):
        # TMP
        return text.upper()
