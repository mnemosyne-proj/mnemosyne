#
# delete_unused_media_files_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_delete_unused_media_files_dlg import \
     Ui_DeleteUnusedMediaFilesDlg


class DeleteUnusedMediaFilesDlg(QtWidgets.QDialog, Ui_DeleteUnusedMediaFilesDlg,
                                Component):

    def __init__(self, **kwds):
        super().__init__(**kwds)
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
        QtWidgets.QDialog.accept(self)





