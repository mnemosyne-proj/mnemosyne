#
# delete_unused_media_files_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_delete_unused_media_files_dlg import \
     Ui_DeleteUnusedMediaFilesDlg


class DeleteUnusedMediaFilesDlg(QtGui.QDialog, Ui_DeleteUnusedMediaFilesDlg,
                                Component):

    def __init__(self, component_manager, unused_media_files):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.unused_media_files = unused_media_files
        self.file_list.setText("\n".join(self.unused_media_files))

    def activate(self):
        self.exec_()

    def accept(self):
        self.database().delete_unused_media_files(self.unused_media_files)
        QtGui.QDialog.accept(self)





