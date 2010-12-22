#
# card_type_tree_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion


class CardTypesTreeWdgt(QtGui.QWidget, Component):

    """Displays all the card types in a tree together with check boxes."""

    def __init__(self, component_manager, parent):
        Component.__init__(self, component_manager)
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QVBoxLayout(self)
        self.card_type_tree = QtGui.QTreeWidget(self)
        self.card_type_tree.setHeaderHidden(True)
        self.layout.addWidget(self.card_type_tree)

    def display(self, criterion=None):
        # Create criterion if needed.
        if criterion is None:
            criterion = DefaultCriterion(self.component_manager)
        # Determine number of cards at each level of the tree.
        root_count = 0
        count_for_card_type = {}
        count_for_fact_view = {}
        for card_type in self.card_types():
            card_type_count = 0
            for fact_view in card_type.fact_views:
                count = \
                    self.database().total_card_count_for_fact_view(fact_view)
                card_type_count += count
                count_for_fact_view[fact_view] = count
            count_for_card_type[card_type] = card_type_count 
            root_count += card_type_count
        # Fill widget.
        self.card_type_tree.clear()
        self.card_type_fact_view_ids_for_node_item = {}
        root_item = QtGui.QTreeWidgetItem(self.card_type_tree,
            [_("All card types (%d)" % (root_count, ))], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
        root_item.setCheckState(0, QtCore.Qt.Checked)
        for card_type in self.card_types():
            card_type_item = QtGui.QTreeWidgetItem(root_item, ["%s (%d)" % \
                (card_type.name, count_for_card_type[card_type])], 0)
            card_type_item.setFlags(card_type_item.flags() | \
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)            
            card_type_item.setCheckState(0, QtCore.Qt.Checked)
            for fact_view in card_type.fact_views:
                fact_view_item = QtGui.QTreeWidgetItem(card_type_item,
                    ["%s (%d)" % (fact_view.name,
                    count_for_fact_view[fact_view])], 0)
                fact_view_item.setFlags(fact_view_item.flags() | \
                    QtCore.Qt.ItemIsUserCheckable)
                if (card_type.id, fact_view.id) in \
                    criterion.deactivated_card_type_fact_view_ids:
                    check_state = QtCore.Qt.Unchecked
                else:
                    check_state = QtCore.Qt.Checked
                fact_view_item.setCheckState(0, check_state)
                self.card_type_fact_view_ids_for_node_item[fact_view_item] = \
                    (card_type.id, fact_view.id)
        self.card_type_tree.expandAll()

    def selection_to_criterion(self, criterion):
        criterion.deactivated_card_type_fact_view_ids = set()
        for item, card_type_fact_view_ids in \
                self.card_type_fact_view_ids_for_node_item.iteritems():
            if item.checkState(0) == QtCore.Qt.Unchecked:
                criterion.deactivated_card_type_fact_view_ids.add(\
                    card_type_fact_view_ids)
        return criterion
