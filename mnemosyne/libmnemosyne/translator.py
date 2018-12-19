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

    def show_dialog(self, card_type, foreign_text):

        """Returns translated text to insert."""

        dialog = self.gui_components[0](\
            translator=self, component_manager=self.component_manager)
        self.component_manager.register(dialog)
        dialog.activate(card_type, foreign_text)
        self.instantiated_gui_components.append(component)
        return dialog.text_to_insert
