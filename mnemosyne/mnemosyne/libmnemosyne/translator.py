#
# translator.py <Peter.Bienstman@UGent.be>
#               <Johannes.Baiter@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component

_ = lambda s: s

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
    global os, gettext
    import os
    import gettext

    def activate(self):

        # We need to monkey-patch the gettext module to provide support for
        # Launchpad's translation infrastructure, as the path for the message
        # catalogs is fixed in the standard library.
        def find_(domain, localedir=None, languages=None, all=0):
            # Get some reasonable defaults for arguments that were not supplied
            if localedir is None:
                localedir = gettext._default_localedir
            if languages is None:
                languages = []
                for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
                    val = os.environ.get(envar)
                    if val:
                        languages = val.split(':')
                        break
                if 'C' not in languages:
                    languages.append('C')
            # now normalize and expand the languages
            nelangs = []
            for lang in languages:
                for nelang in gettext._expand_lang(lang):
                    if nelang not in nelangs:
                        nelangs.append(nelang)
            # select a language
            if all:
                result = []
            else:
                result = None
            for lang in nelangs:
                if lang == 'C':
                    break
                mofile = os.path.join(localedir, '%s.mo' % lang)
                if os.path.exists(mofile):
                    if all:
                        result.append(mofile)
                    else:
                        return mofile
            return result
        gettext.find = find_

        self.change_language(self.config()["ui_language"])
        global _
        _ = self

    def change_language(self, lang):
        if not lang:
            lang = ''
        self._gettext = gettext.translation('mnemosyne', localedir='po',
                    languages=[lang], fallback=True)

    def __call__(self, text):
        try:
            return self._gettext.gettext(text)
        except:
            return text
