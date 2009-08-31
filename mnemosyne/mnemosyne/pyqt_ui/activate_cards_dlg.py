#
# activate_cards_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.pyqt_ui.ui_activate_cards_dlg import Ui_ActivateCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog


class ActivateCardsDlg(QtGui.QDialog, Ui_ActivateCardsDlg,
                       ActivateCardsDialog):

    def __init__(self, component_manager):
        # TODO: compact
        ActivateCardsDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        for card_type in self.card_types():
            a = QtGui.QTreeWidgetItem(0)
            a.setFlags(a.flags() | QtCore.Qt.ItemIsUserCheckable)
            a.setText(0, card_type.name)
            a.setCheckState(0, QtCore.Qt.Checked)
            for fact_view in card_type.fact_views:
                b = QtGui.QTreeWidgetItem(0)
                b.setFlags(b.flags() | QtCore.Qt.ItemIsUserCheckable)
                b.setText(0, fact_view.name)
                b.setCheckState(0, QtCore.Qt.Checked)
                a.addChild(b)
            self.card_types_tree.addTopLevelItem(a)
        self.card_types_tree.expandAll()
        
    def activate(self):
        self.exec_()
        

