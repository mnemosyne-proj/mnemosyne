#
# intro_wizard_dlg.py <Johannes.Baiter@gmail.com>
#

from PyQt4 import QtGui, QtCore

from mnemosyne.pyqt_ui.ui_intro_wizard_dlg import Ui_IntroWizard
from mnemosyne.libmnemosyne.ui_components.dialogs import GettingStartedDialog

class GettingStartedDlg(QtGui.QWizard, Ui_IntroWizard, GettingStartedDialog):

    def __init__(self, component_manager):
        GettingStartedDialog.__init__(self, component_manager)
        QtGui.QWizard.__init__(self, self.main_widget())
        watermark = QtGui.QPixmap("pixmaps/mnemosyne.svg").scaledToHeight(
                300, QtCore.Qt.SmoothTransformation)
        self.setPixmap(QtGui.QWizard.WatermarkPixmap, watermark)
        self.connect(self, QtCore.SIGNAL('finished(int)'), self.finished)
        self.setupUi(self)

    def activate(self):
        GettingStartedDialog.activate(self)
        self.show()

    def finished(self, result):
        if result != 1:
            return
        if self.upload_box.isChecked():
            self.config()["upload_science_logs"] = True
        else:
            self.config()["upload_science_logs"] = False
