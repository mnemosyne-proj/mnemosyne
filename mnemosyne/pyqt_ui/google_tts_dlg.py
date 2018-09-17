#
# google_tts_dlg.py <Peter.Bienstman@UGent.be>
#

import os
from PyQt5 import QtGui, QtCore, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.dialogs import PronouncerDialog
from mnemosyne.pyqt_ui.ui_google_tts_dlg import Ui_GoogleTTSDlg


class GoogleTTSDlg(QtWidgets.QDialog, PronouncerDialog, Ui_GoogleTTSDlg):

    used_for = "ar"  # TMP

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)

    def activate(self, card_type, foreign_text):
        PronouncerDialog.activate(self)
        fact_key = self.config().card_type_property(\
            "foreign_fact_key", card_type, default="")
        font_string = self.config().card_type_property(\
            "font", card_type, fact_key)
        if font_string:
            font = QtGui.QFont()
            font.fromString(font_string)
            self.foreign_text.setCurrentFont(font)
        self.foreign_text.setPlainText(foreign_text)
        self.exec_()

    def browse(self):
        export_dir = self.config()["export_dir"]
        filename = self.main_widget().get_filename_to_save(export_dir,
            _(self.format().filename_filter))
        self.filename_box.setText(filename)
        if filename:
            self.config()["export_dir"] = os.path.dirname(filename)

    def accept(self):
        filename = self.filename_box.text()
        if not filename:
            return QtWidgets.QDialog.accept(self)
        # TODO: process information
        QtWidgets.QDialog.accept(self)
