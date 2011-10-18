#
# gettext_translator.py <Johannes.Baiter@gmail.com>
#

from mnemosyne.libmnemosyne.translator import Translator

import os
import sys
import gettext


class GetTextTranslator(Translator):

    def __init__(self, component_manager):
        Translator.__init__(self, component_manager)
        # Check if we're running in a development environment.
        if os.path.exists("mo"):
            self.lang_path = "mo"
        else:
            self.lang_path = os.path.join(sys.exec_prefix, "share", "locale")

    def supported_languages(self):
        return [os.path.split(x)[1] for x in os.listdir(self.lang_path) \
            if os.path.isdir(os.path.join(self.lang_path, x)) \
            and "mnemosyne.mo" in os.listdir(\
            os.path.join(self.lang_path, x, "LC_MESSAGES"))]

    def set_translator(self, language):
        self._translator = gettext.translation("mnemosyne",
            localedir=self.lang_path, languages=[language],
            fallback=True).ugettext


