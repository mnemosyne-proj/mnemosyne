#
# delete_unused_media_files_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_delete_unused_media_files_dlg import \
     Ui_DeleteUnusedMediaFilesDlg


class DeleteUnusedMediaFilesDlg(QtWidgets.QDialog, Component,
                                Ui_DeleteUnusedMediaFilesDlg):

    def __init__(self, unused_media_files, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.unused_media_files = unused_media_files
        self.file_list.setText("\n".join(self.unused_media_files))

    def activate(self):
        Component.activate(self)
        self.exec()

    def accept(self):
        self.database().delete_unused_media_files(self.unused_media_files)
        QtWidgets.QDialog.accept(self)





