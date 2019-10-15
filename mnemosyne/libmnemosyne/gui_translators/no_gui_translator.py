#
# no_gui_translator.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.gui_translator import GuiTranslator


class NoGuiTranslator(GuiTranslator):

    def set_translator(self, language):
        pass

