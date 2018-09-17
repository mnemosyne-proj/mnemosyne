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

    def activate_dialog(self, foreign_text):
        return self.component_manager.current("pronouncer_dialog",
            used_for=self.__class__).activate(self, foreign_text)

    def pronounce(self, card_type, foreign_text):

        """Should return html text with the correct sound tags and download
        the required the sound files.

        """

        raise NotImplementedError

