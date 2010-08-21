#
# criterion_wdgt_default.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_components.activity_criterion_widget \
     import ActivityCriterionWidget
from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
     DefaultCriterion
from mnemosyne.pyqt_ui.ui_criterion_wdgt_default import Ui_DefaultCriterionWdgt


class DefaultCriterionWdgt(QtGui.QWidget, Ui_DefaultCriterionWdgt,
                           ActivityCriterionWidget):

    """Note that this dialog can support active tags and forbidden tags,
    but not at the same time, in order to keep the interface compact.

    """

    used_for = DefaultCriterion

    def __init__(self, component_manager, parent):
        ActivityCriterionWidget.__init__(self, component_manager)
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.parent_saved_sets = parent.saved_sets

    def display_default_criterion(self):
        criterion = DefaultCriterion(self.component_manager)
        for tag in self.database().tags():
            criterion.active_tag__ids.add(tag._id)
        self.display_criterion(criterion)
    
    def display_criterion(self, criterion):
        # Fill card types tree widget.
        self.card_types_tree.clear()
        self.card_type_fact_view_ids_for_node_item = {}
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
                if (card_type.id, fact_view.id) in \
                    criterion.deactivated_card_type_fact_view_ids:
                    check_state = QtCore.Qt.Unchecked
                else:
                    check_state = QtCore.Qt.Checked
                fact_view_item.setCheckState(0, check_state)
                self.card_type_fact_view_ids_for_node_item[fact_view_item] = \
                    (card_type.id, fact_view.id)
        self.card_types_tree.expandAll()
        # Fill tags tree widget.
        self.tags_tree.clear()
        self.tag_for_node_item = {}
        root_item = QtGui.QTreeWidgetItem(self.tags_tree, [_("All tags")], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
        root_item.setCheckState(0, QtCore.Qt.Checked)
        self.tag_for_node_item = {}
        node_item_for_partial_tag = {}
        for tag in self.database().all_tags():
            if tag.name == "__UNTAGGED__":
                tag.name = _("Untagged")
            parent = root_item
            partial_tag = ""
            node_item = None
            for node in tag.name.split("::"):
                node += "::"
                partial_tag += node
                if partial_tag not in node_item_for_partial_tag:
                    node_item = QtGui.QTreeWidgetItem(parent, [node[:-2]], 0)
                    node_item.setFlags(node_item.flags() | \
                        QtCore.Qt.ItemIsUserCheckable | \
                        QtCore.Qt.ItemIsTristate)
                    node_item_for_partial_tag[partial_tag] = node_item
                parent = node_item_for_partial_tag[partial_tag]
            self.tag_for_node_item[node_item] = tag
        # Set forbidden tags.
        if len(criterion.forbidden_tag__ids):
            self.active_or_forbidden.setCurrentIndex(1)
            for node_item, tag in self.tag_for_node_item.iteritems():
                if tag._id in criterion.forbidden_tag__ids:
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.Unchecked)  
        # Set active tags.
        else:
            self.active_or_forbidden.setCurrentIndex(0)
            for node_item, tag in self.tag_for_node_item.iteritems():
                if tag._id in criterion.active_tag__ids:
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.Unchecked)
        # Finalise.
        self.tags_tree.sortItems(0, QtCore.Qt.AscendingOrder)
        self.tags_tree.expandAll()

        
    def criterion(self):

        """Build the criterion from the information the user entered in the
        widget.

        """
        
        criterion = DefaultCriterion(self.component_manager)
        # Card types and fact views.
        for item, card_type_fact_view_ids in \
                self.card_type_fact_view_ids_for_node_item.iteritems():
            if item.checkState(0) == QtCore.Qt.Unchecked:
                criterion.deactivated_card_type_fact_view_ids.add(\
                    card_type_fact_view_ids)
        # Tag tree contains active tags.
        if self.active_or_forbidden.currentIndex() == 0: 
            for item, tag in self.tag_for_node_item.iteritems():
                if item.checkState(0) == QtCore.Qt.Checked:
                    criterion.active_tag__ids.add(tag._id)
            criterion.forbidden_tags = set()
        # Tag tree contains forbidden tags.
        else:
            for item, tag in self.tag_for_node_item.iteritems():
                if item.checkState(0) == QtCore.Qt.Checked:
                    criterion.forbidden_tag__ids.add(tag._id)
            criterion.active_tags = set(self.tag_for_node_item.values())
        return criterion

    def criterion_changed(self):
        self.parent_saved_sets.clearSelection()
