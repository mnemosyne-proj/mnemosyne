#
# card_set_name_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_component import UiComponent
from mnemosyne.pyqt_ui.ui_card_set_name_dlg import Ui_CardSetNameDlg


class CardSetNameDlg(QtGui.QDialog, Ui_CardSetNameDlg, UiComponent):

    def __init__(self, component_manager, criterion):
        UiComponent.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.criterion = criterion

    def accept(self):
        self.criterion.name = unicode(self.set_name.text())
        self.database().add_activity_criterion(self.criterion)
        return QtGui.QDialog.accept(self)
        
