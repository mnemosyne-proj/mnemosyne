#
# pronouncer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Pronouncer(Component):

    """Generic text-to-speech service for words and sentences. """

    component_type = "pronouncer"
    used_for = None  # ISO 639-1 code
    popup_menu_text = None # "Insert translation..."

    def download_tmp_audio_file(self, card_type, foreign_text):

        """Returns a temporary filename with the audio."""

        raise NotImplementedError

    def show_dialog(self, card_type, foreign_text):

        """Returns html audio tag to insert."""

        dialog = self.gui_components[0](\
            pronouncer=self, component_manager=self.component_manager)
        self.component_manager.register(dialog)
        dialog.activate(card_type, foreign_text)
        self.instantiated_gui_components.append(component)
        return dialog.text_to_insert

