#
# add_tags_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.pyqt_ui.add_cards_dlg import AddEditCards
from mnemosyne.pyqt_ui.ui_add_tags_dlg import Ui_AddTagsDlg


class AddTagsDlg(QtGui.QDialog, Ui_AddTagsDlg, AddEditCards):

    def __init__(self, component_manager, return_values):
        AddEditCards.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)        
        self.return_values = return_values
        self.update_tags_combobox("")
        
    def accept(self):
        self.return_values["tag_names"] = [c.strip() for c in \
                     unicode(self.tags.currentText()).split(',')]
        return QtGui.QDialog.accept(self)
    
