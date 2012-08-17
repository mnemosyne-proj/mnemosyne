#
# export_metadata_dlg.py <Peter.Bienstman@UGent.be>
#

import os
from PyQt4 import QtGui, QtCore

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_import_dlg import Ui_ImportDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ExportDialog


class ImportDlg(QtGui.QDialog, Ui_ImportDlg, ImportDialog):

    def __init__(self, component_manager):
        ImportDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        # File formats.
        i = 0
        current_index = None
        for format in self.component_manager.all("file_format"):
            self.file_formats.addItem(_(format.description))
            if type(format) == self.config()["export_format"]:
                current_index = i
            i += 1
        if current_index is not None:
            self.file_formats.setCurrentIndex(current_index)

    def file_format_changed(self):
        self.filename_box.setText("")

    def activate(self):
        ImportDialog.activate(self)
        self.exec_()

    def format(self):
        for _format in self.component_manager.all("file_format"):
            if _(_format.description) == \
                unicode(self.file_formats.currentText()):
                return _format

    def browse(self):
        export_dir = self.config()["export_dir"]
        filename = self.main_widget().get_filename_to_open(export_dir,
            _(self.format().filename_filter))
        self.filename_box.setText(filename)
        if filename:
            self.config()["export_dir"] = os.path.dirname(filename)

    def accept(self):
        filename = unicode(self.filename_box.text())
        if filename:
            if os.path.exists(filename):
                answer = self.main_widget().show_question(\
                _("File exists. Overwrite?"), _("Yes"))
            self.config()["export_format"] = type(self.format())
            self.format().do_export(filename, extra_tag_name)
            QtGui.QDialog.accept(self)
        else:
            self.main_widget().show_error(_("File does not exist."))
