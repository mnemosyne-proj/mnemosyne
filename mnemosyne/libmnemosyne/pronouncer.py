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

    def pronounce(self, text):

        """Should return html text with the correct sound tags and download
        the required the sound files.

        """

        raise NotImplementedError
