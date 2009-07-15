#
# progress_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.ui_components.dialogs import ProgressDialog


class ProgressDlg(ProgressDialog, QtGui.QProgressDialog):

    def __init__(self, component_manager):
        ProgressDialog.__init__(self, component_manager)
        QtGui.QProgressDialog.__init__(self, self.main_widget())
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setCancelButton(None)

    def set_range(self, minimum, maximum):
        self.setRange(minimum, maximum)
        
    def set_text(self, text):
        self.setLabelText(text)

    def set_value(self, value):
        self.setValue(value)

