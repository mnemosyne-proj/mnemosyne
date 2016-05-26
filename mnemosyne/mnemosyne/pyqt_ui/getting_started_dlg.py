#
# intro_wizard_dlg.py <Johannes.Baiter@gmail.com>
#

from PyQt5 import QtGui, QtCore, QtWidgets

from mnemosyne.pyqt_ui.ui_getting_started_dlg import Ui_GettingStartedDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import GettingStartedDialog

class GettingStartedDlg(QtWidgets.QWizard, Ui_GettingStartedDlg,
        GettingStartedDialog):

    def __init__(self, component_manager):
        super().__init__(self.main_widget(), component_manager=component_manager)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        # Note: the svg file does not seem to work under windows.
        #watermark = QtGui.QPixmap(":/mnemosyne/pixmaps/mnemosyne.svg")\
        #    .scaledToHeight(200, QtCore.Qt.SmoothTransformation)
        watermark = QtGui.QPixmap(":/mnemosyne/pixmaps/mnemosyne.png")
        self.setPixmap(QtWidgets.QWizard.WatermarkPixmap, watermark)

    def activate(self):
        GettingStartedDialog.activate(self)
        self.show()

    def accept(self):
        self.config()["upload_science_logs"] = self.upload_box.isChecked()
        QtWidgets.QWizard.accept(self)

