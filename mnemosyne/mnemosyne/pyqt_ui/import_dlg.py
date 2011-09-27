#
# import_dlg.py <Johannes.Baiter@gmail.com>
#

from PyQt4 import QtGui, QtCore

from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.pyqt_ui.ui_import_dlg import Ui_ImportDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog


class ImportDlg(QtGui.QDialog, Ui_ImportDlg, ImportDialog):
    
    def __init__(self, component_manager):
        ImportDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        for format in self.component_manager.all("file_format"):
            self.file_formats.addItem(format.description)
        for tag in self.database().tags():
            self.tags.addItem(tag.name)

    def activate(self):
        self.exec_()

    def format(self):
        for _format in self.component_manager.all("file_format"):
            if _format.description == self.file_formats.currentText():
                return _format

    def browse(self):
        path = expand_path(self.config()["import_dir"], self.config().data_dir)
        self.filename.setText(self.main_widget().get_filename_to_open(path,
            self.format().filename_filter))

    def accept(self):
        self.format().do_import(unicode(self.filename.text()))
        QtGui.QDialog.accept(self)
