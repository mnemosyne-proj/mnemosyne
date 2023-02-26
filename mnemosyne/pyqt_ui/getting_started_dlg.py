#
# intro_wizard_dlg.py <Johannes.Baiter@gmail.com>
#

from PyQt6 import QtGui, QtCore, QtWidgets

from mnemosyne.pyqt_ui.ui_getting_started_dlg import Ui_GettingStartedDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import GettingStartedDialog

class GettingStartedDlg(QtWidgets.QWizard, GettingStartedDialog, 
                        Ui_GettingStartedDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        # Note: the svg file does not seem to work under windows.
        #watermark = QtGui.QPixmap("pixmaps/mnemosyne.svg")\
        #    .scaledToHeight(200, QtCore.Qt.TransformationMode.SmoothTransformation)
        watermark = QtGui.QPixmap("icons:mnemosyne.png")
        self.setPixmap(QtWidgets.QWizard.WizardPixmap.WatermarkPixmap, watermark)

    def activate(self):
        GettingStartedDialog.activate(self)
        self.exec()

    def accept(self):
        self.config()["upload_science_logs"] = self.upload_box.isChecked()
        QtWidgets.QWizard.accept(self)

