#
# activate_cards_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.pyqt_ui.ui_activate_cards_dlg import Ui_ActivateCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog


class ActivateCardsDlg(QtGui.QDialog, Ui_ActivateCardsDlg,
                       ActivateCardsDialog):

    def __init__(self, component_manager):
        ActivateCardsDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        # Fill card type tree widget.
        for card_type in self.card_types():
            card_type_item = QtGui.QTreeWidgetItem(self.card_types_tree,
                                                   [card_type.name], 0)
            card_type_item.setFlags(card_type_item.flags() | \
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
            card_type_item.setCheckState(0, QtCore.Qt.Checked)
            for fact_view in card_type.fact_views:
                fact_view_item = QtGui.QTreeWidgetItem(card_type_item,
                                                       [fact_view.name], 0)
                fact_view_item.setFlags(fact_view_item.flags() | \
                    QtCore.Qt.ItemIsUserCheckable)
                fact_view_item.setCheckState(0, QtCore.Qt.Checked)
        self.card_types_tree.expandAll()
        # Fill tags tree widget.
        nodes_at_level = {} # TODO: rename + document + remove level
        for tag in ["a", "b", "a::b", "a::c", "b::c::d"]:
            parent = self.tags_tree
            partial_tag = ""
            for level, node in enumerate(tag.split("::")):
                node += "::"
                partial_tag += node
                if level not in nodes_at_level:
                    nodes_at_level[level] = {}
                if node not in nodes_at_level[level]:
                    node_item = QtGui.QTreeWidgetItem(parent, [node[:-2]], 0)
                    node_item.setFlags(node_item.flags() | \
                        QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                    nodes_at_level[level][partial_tag] = node_item
                parent = nodes_at_level[level][partial_tag]
        self.tags_tree.expandAll()
        # TODO: sort
                
        
    def activate(self):
        self.exec_()
        

