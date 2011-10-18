#
# qt_translator.py <Johannes.Baiter@gmail.com>
#

import os
import sys

from PyQt4.QtCore import QTranslator, QCoreApplication
    
from mnemosyne.libmnemosyne.translators.gettext_translator \
     import GetTextTranslator


class QtTranslator(GetTextTranslator):

    def translate_ui(self, language):
        # To translate the Qt standard dialogs without obscene amounts of
        # monkey- patching, we have to use Qt's own translation framework.
        app = QCoreApplication.instance()
        qt_translator = QTranslator(app)
        try:
            qtdir = os.environ["QTDIR"]
        except:
            if sys.platform == "win32":
                qtdir = os.path.join(sys.exec_prefix, "share", "qt4")
            else:
                qtdir = os.path.join("/usr", "share", "qt4")
        qm_dir = os.path.join(qtdir, "translations", "qt_" + language + ".qm")
        qt_translator.load(os.path.join(qtdir, "translations",
            "qt_" + language + ".qm"))
        app.installTranslator(qt_translator)

