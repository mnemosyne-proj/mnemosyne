#
# no_translator.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import Translator


class NoTranslator(Translator):

    def set_translator(self, language):
        pass
    
