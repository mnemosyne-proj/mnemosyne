#
# import_dlg.py <Johannes.Baiter@gmail.com>
#

import os
from PyQt4 import QtGui, QtCore

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_import_dlg import Ui_ImportDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog


class ImportDlg(QtGui.QDialog, Ui_ImportDlg, ImportDialog):
    
    def __init__(self, component_manager):
        ImportDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        # File formats.
        i = 0
        current_index = None
        for format in self.component_manager.all("file_format"):
            self.file_formats.addItem(format.description)
            if type(format) == self.config()["import_format"]:
                current_index = i
            i += 1
        if current_index is not None:
            self.file_formats.setCurrentIndex(current_index)             
        # Extra tag.
        i = 0
        current_index = None
        for tag in self.database().tags():
            if tag.name != "__UNTAGGED__":
                self.tags.addItem(tag.name)
                i += 1
            if tag.name == self.config()["import_extra_tag_name"]:
                current_index = i
        if current_index is not None:
            self.tags.setCurrentIndex(current_index)
        if self.config()["import_extra_tag_name"] == "":
            self.tags.insertItem(0, "")
            self.tags.setCurrentIndex(0)

    def file_format_changed(self):
        self.filename_box.setText("")
            
    def activate(self):
        ImportDialog.activate(self)
        self.retranslateUi(self)
        self.exec_()

    def format(self):
        for _format in self.component_manager.all("file_format"):
            if _format.description == self.file_formats.currentText():
                return _format

    def browse(self):
        import_dir = self.config()["import_dir"]
        filename = self.main_widget().get_filename_to_open(import_dir,
            self.format().filename_filter)
        self.filename_box.setText(filename)
        if filename:
            self.config()["import_dir"] = os.path.dirname(filename)
        
    def accept(self):
        filename = unicode(self.filename_box.text())
        if filename and os.path.exists(filename):
            extra_tag_name = unicode(self.tags.currentText())
            self.config()["import_extra_tag_name"] = extra_tag_name
            if not extra_tag_name:
                extra_tag_name = None
            self.config()["import_format"] = type(self.format())
            self.format().do_import(filename, extra_tag_name)
            QtGui.QDialog.accept(self)
        else:
            self.main_widget().show_error(_("File does not exist."))
