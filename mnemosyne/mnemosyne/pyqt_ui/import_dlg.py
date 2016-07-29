#
# import_dlg.py <Johannes.Baiter@gmail.com>
#

import os
from PyQt5 import QtGui, QtCore, QtWidgets

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_import_dlg import Ui_ImportDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog


class ImportDlg(QtWidgets.QDialog, ImportDialog, Ui_ImportDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        # File formats.
        i = 0
        current_index = None
        for format in self.component_manager.all("file_format"):
            if not format.import_possible:
                continue
            self.file_formats.addItem(_(format.description))
            if str(type(format)) == self.config()["import_format"]:
                current_index = i
            i += 1
        if current_index is not None:
            self.file_formats.setCurrentIndex(current_index)
        # Extra tag.
        i = 0
        current_index = None
        for tag in self.database().tags():
            if tag.name == self.config()["import_extra_tag_names"]:
                current_index = i
            if tag.name != "__UNTAGGED__":
                self.tags.addItem(tag.name)
                i += 1
        if current_index is not None:
            self.tags.setCurrentIndex(current_index)
        if self.config()["import_extra_tag_names"] == "":
            self.tags.insertItem(0, "")
            self.tags.setCurrentIndex(0)
        if "," in self.config()["import_extra_tag_names"]:
            self.tags.insertItem(0, self.config()["import_extra_tag_names"])
            self.tags.setCurrentIndex(0)

    def file_format_changed(self):
        self.filename_box.setText("")

    def activate(self):
        ImportDialog.activate(self)
        self.exec_()

    def format(self):
        for _format in self.component_manager.all("file_format"):
            if _(_format.description) == self.file_formats.currentText():
                return _format

    def browse(self):
        import_dir = self.config()["import_dir"]
        filename = self.main_widget().get_filename_to_open(import_dir,
            _(self.format().filename_filter))
        self.filename_box.setText(filename)
        if filename:
            self.config()["import_dir"] = os.path.dirname(filename)

    def accept(self):
        filename = self.filename_box.text()
        if filename and os.path.exists(filename):
            extra_tag_names = self.tags.currentText()
            self.config()["import_extra_tag_names"] = extra_tag_names
            if not extra_tag_names:
                extra_tag_names = None
            self.config()["import_format"] = str(type(self.format()))
            self.format().do_import(filename, extra_tag_names)
            QtWidgets.QDialog.accept(self)
        else:
            self.main_widget().show_error(_("File does not exist."))
