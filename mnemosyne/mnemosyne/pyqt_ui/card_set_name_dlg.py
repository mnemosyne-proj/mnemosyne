#
# card_set_name_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_component import UiComponent
from mnemosyne.pyqt_ui.ui_card_set_name_dlg import Ui_CardSetNameDlg


class CardSetNameDlg(QtGui.QDialog, Ui_CardSetNameDlg, UiComponent):

    def __init__(self, component_manager, criterion, existing_names):
        UiComponent.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.criterion = criterion
        self.existing_names = existing_names
        if self.criterion.name:
            self.set_name.setText(self.criterion.name)
            self.set_name.selectAll()
        else:
            self.ok_button.setEnabled(False)
            
    def text_changed(self):
        if self.set_name.text():
            self.ok_button.setEnabled(True)
        else:
            self.ok_button.setEnabled(False)

    def reject(self):
        self.criterion.name = ""
        return QtGui.QDialog.reject(self)        
        
    def accept(self):
        name = unicode(self.set_name.text())
        if name in self.existing_names:
            self.main_widget().show_error(_("This name already exists."))
            return
        self.criterion.name = name
        return QtGui.QDialog.accept(self)
        