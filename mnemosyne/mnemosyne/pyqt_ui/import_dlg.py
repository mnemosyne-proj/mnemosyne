#
# import_dlg.py <Johannes.Baiter@gmail.com>
#

from PyQt4 import QtGui, QtCore

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.pyqt_ui.ui_import_dlg import Ui_ImportDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ImportDialog

class ImportDlg(QtGui.QDialog, Ui_ImportDlg, ImportDialog):
    
    def __init__(self, component_manager):
        ImportDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        for format in self.component_manager.all("file_format"):
            self.fileformats.addItem(format.description)
        for tag in self.database().tags():
            self.categories.addItem(tag.name)

        self.connect(self.browse_button, QtCore.SIGNAL("clicked()"), self.browse)
        self.connect(self.ok_button,    QtCore.SIGNAL("clicked()"), self.apply)

    def activate(self):
        ImportDialog.activate(self)
        self.show()

    def _get_selected_format(self):
        for format in self.component_manager.all("file_format"):
                if format.description == self.fileformats.currentText():
                    return format

    def browse(self):
        self.importer = self._get_selected_format()
        path = expand_path(self.config()["import_dir"], self.config().data_dir)
        self.fname = self.main_widget().get_filename_to_open(path,
            self.importer.filename_filter)
        self.filename.setText(self.fname)

    def apply(self):
        self.importer.do_import(self.fname)
        review_controller = self.review_controller()
        review_controller.reload_counters()
        if review_controller.card is None:
            review_controller.show_new_question()
        else:
            review_controller.update_status_bar_counters()
        self.done(1)
