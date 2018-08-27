#
# translator.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Translator(Component):

    """Generic translation service for words and sentences. Not to be confused
    the GuiTranslator, which is for translating the user interface.

    """

    component_type = "translator"
    used_for = None  # ISO 639-1 code
    popup_menu_text = None # "Insert translation..."

    def translate(self, text):
        raise NotImplementedError
