#
# google_pronouncer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.pronouncer import Pronouncer


class GooglePronouncer(Pronouncer):

    used_for = "ar"  # TMP
    popup_menu_text = "Insert Google text-to-speech..."

    def pronounce(self, foreign_text):
        # TMP
        return foreign_text.upper()

    def show_dialog(self, card_type, foreign_text):
        dialog = self.component_manager.current\
            ("pronouncer_dialog", used_for=self.used_for)\
            (component_manager=self.component_manager)
        return dialog.activate(card_type, foreign_text)
