#
# pronouncer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Pronouncer(Component):

    """Generic translation service for words and sentences. Not to be confused
    the GuiTranslator, which is for translating the user interface.

    """

    component_type = "pronouncer"
    used_for = None  # ISO 639-1 code
    popup_menu_text = None # "Insert translation..."

    def show_dialog(self, card_type, foreign_text):
         # TODO: used for?
        dialog = self.component_manager.current\
            ("pronouncer_dialog", used_for=self.used_for)\
            (pronouncer=self, component_manager=self.component_manager)
        dialog.activate(card_type, foreign_text)
        return dialog.text_to_insert

    def download_tmp_audio_file(self, card_type, foreign_text):

        """Returns a temporary filename with the audio."""

        raise NotImplementedError
