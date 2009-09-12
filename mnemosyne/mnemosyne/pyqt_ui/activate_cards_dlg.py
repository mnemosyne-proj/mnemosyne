#
# activate_cards_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_activate_cards_dlg import Ui_ActivateCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog
from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
     DefaultCriterion


class ActivateCardsDlg(QtGui.QDialog, Ui_ActivateCardsDlg,
                       ActivateCardsDialog):

    def __init__(self, component_manager):
        ActivateCardsDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        # Restore sizes.
        config = self.config()
        width, height = config["activate_cards_dlg_size"]
        if width:
            self.resize(width, height)
        splitter_sizes = config["activate_cards_dlg_splitter"]
        if not splitter_sizes:
            self.splitter.setSizes([100, 350])
        else:
            self.splitter.setSizes(splitter_sizes)
        # Fill card types tree widget.
        self.card_type_fact_view_for_item = {}
        root_item = QtGui.QTreeWidgetItem(self.card_types_tree,
            [_("All card types")], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
        root_item.setCheckState(0, QtCore.Qt.Checked)
        for card_type in self.card_types():
            card_type_item = QtGui.QTreeWidgetItem(root_item,
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
                self.card_type_fact_view_for_item[fact_view_item] = \
                    (card_type, fact_view)
        self.card_types_tree.expandAll()
        # Fill tags tree widget.
        self.tag_for_item = {}
        root_item = QtGui.QTreeWidgetItem(self.tags_tree, [_("All tags")], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
        root_item.setCheckState(0, QtCore.Qt.Checked)
        self.tag_for_item = {}
        item_for_partial_tag = {}
        for tag in self.database().get_tags():
            parent = root_item
            partial_tag = ""
            node_item = None
            for node in tag.name.split("::"):
                node += "::"
                partial_tag += node
                if partial_tag not in item_for_partial_tag:
                    node_item = QtGui.QTreeWidgetItem(parent, [node[:-2]], 0)
                    node_item.setFlags(node_item.flags() | \
                        QtCore.Qt.ItemIsUserCheckable | \
                        QtCore.Qt.ItemIsTristate)
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                    item_for_partial_tag[partial_tag] = node_item
                parent = item_for_partial_tag[partial_tag]
            self.tag_for_item[node_item] = tag
        self.tags_tree.sortItems(0, QtCore.Qt.AscendingOrder)
        self.tags_tree.expandAll()                
        
    def activate(self):
        self.exec_()

    def _store_layout(self):
        self.config()["activate_cards_dlg_size"] = \
            (self.width(), self.height())
        self.config()["activate_cards_dlg_splitter"] = \
            self.splitter.sizes()
        
    def closeEvent(self, event):
        self._store_layout()
        
    def accept(self):
        criterion = DefaultCriterion(self.component_manager)
        # Card types and fact views.
        for item, card_type_fact_view in \
                self.card_type_fact_view_for_item.iteritems():
            if item.checkState(0) == QtCore.Qt.Unchecked:
                criterion.deactivated_card_type_fact_views.add(\
                    card_type_fact_view)
        # Tag tree contains required tags.
        # (Note that we don't expose the functionality in the GUI to set
        # required and forbidden tags separately.)
        if self.combobox.currentIndex() == 0: 
            for item, tag in self.tag_for_item.iteritems():
                if item.checkState(0) == QtCore.Qt.Checked:
                    criterion.required_tags.add(tag)
            criterion.forbidden_tags = set()
        # Tag tree contains forbidden tags.
        else:
            for item, tag in self.tag_for_item.iteritems():
                if item.checkState(0) == QtCore.Qt.Checked:
                    criterion.forbidden_tags.add(tag)
            criterion.required_tags = set(self.tag_for_item.values())
        # Apply.
        self.database().set_current_activity_criterion(criterion)
        self._store_layout()
        return QtGui.QDialog.accept(self)

    def reject(self):
        self._store_layout()
        QtGui.QDialog.reject(self)
