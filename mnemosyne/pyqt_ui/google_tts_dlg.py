#
# google_tts_dlg.py <Peter.Bienstman@UGent.be>
#

import os
from PyQt5 import QtGui, QtCore, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.dialogs import PronouncerDialog
from mnemosyne.pyqt_ui.ui_google_tts_dlg import Ui_GoogleTTSDlg


class GoogleTTSDlg(QtWidgets.QDialog, ExportDialog, Ui_GoogleTTSDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)

    def activate(self):
        ExportDialog.activate(self)
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
