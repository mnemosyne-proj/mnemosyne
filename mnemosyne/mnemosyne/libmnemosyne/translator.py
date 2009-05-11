#
# translator.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Translator(Component):

    component_type = "translator"

    def translate(self, text):
        raise NotImplementedError


class NoTranslation(Translator):

    def translate(self, text):
        return text


class GetTextTranslator(Translator):

    def translate(self, text):
        import gettext
        return gettext.gettext(text)
    
