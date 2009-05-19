#
# translator.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component

_ = None

class Translator(Component):

    component_type = "translator"

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        global _
        _ = self

    def __call__(self, text):
        raise NotImplementedError


class NoTranslation(Translator):

    def __call__(self, text):
        return text


class GetTextTranslator(Translator):

    def __call__(self, text):
        import gettext
        return gettext.gettext(text)
