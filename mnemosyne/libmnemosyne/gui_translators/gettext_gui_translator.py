#
# gettext_gui_translator.py <Johannes.Baiter@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import GuiTranslator

import os
import sys
import gettext


class GetTextGuiTranslator(GuiTranslator):

    def __init__(self, component_manager):
        GuiTranslator.__init__(self, component_manager)
        # Check if we're running in a development environment.
        if os.path.exists("mo"):
            self.lang_path = "mo"
        else:  # pragma: no cover
            self.lang_path = os.path.join(sys.exec_prefix, "share", "locale")

    def supported_languages(self):
        try:
            return [os.path.split(x)[1] for x in os.listdir(self.lang_path) \
            if os.path.isdir(os.path.join(self.lang_path, x)) and \
            os.path.exists(os.path.join(self.lang_path, x, "LC_MESSAGES")) \
            and "mnemosyne.mo" in os.listdir(\
            os.path.join(self.lang_path, x, "LC_MESSAGES"))]
        except:
            return []

    def set_translator(self, language):
        self._translator = gettext.translation("mnemosyne",
            localedir=self.lang_path, languages=[language],
            fallback=True).gettext

