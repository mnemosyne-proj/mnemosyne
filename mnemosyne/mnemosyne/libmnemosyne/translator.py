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
    global gettext, os, sys
    import gettext
    import os
    import sys

    def activate(self):
        # We need to monkey-patch the gettext module to provide support for
        # Launchpad's translation infrastructure, as the path for the message
        # catalogs is fixed in the standard library.

        self.change_language(self.config()["ui_language"])
        global _
        _ = self

    def change_language(self, lang):
        if not lang:
            lang = ''
        # Check if we're running in a development environment
        if os.path.exists('mo'):
            localedir = 'mo'
        else:
            localedir = os.path.join(sys.exec_prefix, "share", "locale")
        self._gettext = gettext.translation('mnemosyne', localedir=localedir,
                    languages=[lang], fallback=True)

    def get_supported_languages(self):
        import glob
        if os.path.exists('mo'):
            langs = [os.path.split(x)[1] for x in glob.glob(os.path.join(
                     'mo', '*')) if os.path.isdir(x)
                     and len(os.path.split(x)[1]) == 2]
        else:
            if sys.platform == 'win32':
                path_separator = "\\"
            else:
                path_separator = "/"
            langs = [x.split(path_separator)[-3] for x in glob.glob(
                     os.path.join(sys.exec_prefix, "share", "locale", '*',
                                  'LC_MESSAGES', 'mnemosyne.mo'))]
            print langs
        return langs

    def __call__(self, text):
        try:
            return self._gettext.gettext(text)
        except:
            return text
