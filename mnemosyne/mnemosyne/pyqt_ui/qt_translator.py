#
# qt_translator.py <Johannes.Baiter@gmail.com>
#

import os
import sys

from PyQt4.QtCore import QTranslator, QCoreApplication

from mnemosyne.libmnemosyne.translators.gettext_translator \
     import GetTextTranslator


class QtTranslator(GetTextTranslator):

    """This deals with translating Qt itself. The rest of the strings are
    still translated using the gettext mechanism, as we've modified pyuic4
    to use gettext too.

    """

    def __init__(self, component_manager):
        GetTextTranslator.__init__(self, component_manager)
        self.qt_translator = QTranslator(QCoreApplication.instance())
        try:
            self.qt_dir = os.environ["QTDIR"]
        except:
            if sys.platform == "win32":
                self.qt_dir = os.path.join(sys.exec_prefix, "share", "qt4")
            else:
                self.qt_dir = os.path.join("/usr", "share", "qt4")

    def translate_ui(self, language):
        app = QCoreApplication.instance()
        # We always need to remove a translator, to make sure we generate a
        # LanguageChange event even if their is no Qt translation for that
        # language installed.
        app.removeTranslator(self.qt_translator)
        self.qt_translator.load(os.path.join(self.qt_dir, "translations",
            "qt_" + language + ".qm"))
        app.installTranslator(self.qt_translator)

