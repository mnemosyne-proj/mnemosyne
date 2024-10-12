#
# translator.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component


class Translator(Component):

    """Generic translation service for words and sentences. Not to be confused
    the GuiTranslator, which is for translating the user interface.

    Note that a single component can handle multiple languages (e.g. Google TTS)
    and the language to be used will be determined through the language_id
    property of the card_type argument.

    """

    component_type = "translator"
    used_for = None # Single ISO 639-1 code, or multiple as tuple of strings.
    popup_menu_text = None # "Insert translation..."

    def translate(self, card_type, foreign_text, dest_language_id):

        """Returns translated text."""

        raise NotImplementedError

    def show_dialog(self, card_type, foreign_text):

        """Returns translated text to insert. The user can set the target
        language in the dialog."""

        dialog = self.gui_components[0](\
            translator=self, component_manager=self.component_manager)
        self.component_manager.register(dialog)
        dialog.activate(card_type, foreign_text)
        self.instantiated_gui_components.append(dialog)
        return dialog.text_to_insert
