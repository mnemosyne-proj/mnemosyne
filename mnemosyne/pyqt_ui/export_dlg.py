#
# export_dlg.py <Peter.Bienstman@gmail.com>
#

import os
from PyQt6 import QtGui, QtCore, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_export_dlg import Ui_ExportDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ExportDialog


class ExportDlg(QtWidgets.QDialog, ExportDialog, Ui_ExportDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        # File formats.
        i = 0
        current_index = None
        for format in self.component_manager.all("file_format"):
            if not format.export_possible:
                continue
            self.file_formats.addItem(_(format.description))
            if str(type(format)) == self.config()["export_format"]:
                current_index = i
            i += 1
        if current_index is not None:
            self.file_formats.setCurrentIndex(current_index)

    def file_format_changed(self):
        filename = self.filename_box.text()
        if "." in filename:
            filename = filename.rsplit(".")[0] + self.format().extension
            self.filename_box.setText(filename)

    def activate(self):
        ExportDialog.activate(self)
        self.exec()

    def format(self):
        for _format in self.component_manager.all("file_format"):
            if _(_format.description) == self.file_formats.currentText():
                return _format

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
        if not filename.endswith(self.format().extension):
            filename += self.format().extension
        self.config()["export_format"] = str(type(self.format()))
        result = self.format().do_export(filename)
        if result != -1:  # Cancelled.
            self.main_widget().show_information(_("Done!"))
        QtWidgets.QDialog.accept(self)
