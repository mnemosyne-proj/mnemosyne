#
# tag_tree_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.tag_tree import TagTree
from mnemosyne.libmnemosyne.component import Component


class TagsTreeWdgt(QtGui.QWidget, Component):

    """Displays all the tags in a tree together with check boxes."""

    def __init__(self, component_manager, parent):
        Component.__init__(self, component_manager)
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QVBoxLayout(self)
        self.tag_tree_wdgt = QtGui.QTreeWidget(self)
        self.tag_tree_wdgt.setHeaderHidden(True)
        self.layout.addWidget(self.tag_tree_wdgt)

    def create_tree(self, tree, qt_parent):
        for node in tree:
            node_name = "%s (%d)" % \
                (self.tag_tree.display_name_for_node[node],
                self.tag_tree.card_count_for_node[node])
            node_item = QtGui.QTreeWidgetItem(qt_parent, [node_name], 0)
            node_item.setFlags(node_item.flags() | \
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
            if type(node) == type([]):
                self.create_tree(tree=node, qt_parent=node_item)
            else:
                self.tag_for_node_item[node_item] = \
                    self.database().get_or_create_tag_with_name(node)
        
    def display(self, criterion):
        # Create tree.
        self.tag_tree_wdgt.clear()
        self.tag_for_node_item = {}
        self.tag_tree = TagTree(self.component_manager)
        node = "__ALL__"
        node_name = "%s (%d)" % (self.tag_tree.display_name_for_node[node],
            self.tag_tree.card_count_for_node[node])
        root = self.tag_tree.tree[node]
        root_item = QtGui.QTreeWidgetItem(self.tag_tree_wdgt, [node_name], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
        root_item.setCheckState(0, QtCore.Qt.Checked)
        self.create_tree(self.tag_tree.tree[node], qt_parent=root_item)            
        # Set forbidden tags.
        if len(criterion.forbidden_tag__ids):
            for node_item, tag in self.tag_for_node_item.iteritems():
                if tag._id in criterion.forbidden_tag__ids:
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.Unchecked)  
        # Set active tags.
        else:
            for node_item, tag in self.tag_for_node_item.iteritems():
                if tag._id in criterion.active_tag__ids:
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.Unchecked)
        # Finalise.
        self.tag_tree_wdgt.expandAll()

    def selection_to_active_tags_in_criterion(self, criterion):
        for item, tag in self.tag_for_node_item.iteritems():
            if item.checkState(0) == QtCore.Qt.Checked:
                criterion.active_tag__ids.add(tag._id)
        criterion.forbidden_tags = set()
        return criterion

    def selection_to_forbidden_tags_in_criterion(self, criterion):
        for item, tag in self.tag_for_node_item.iteritems():
            if item.checkState(0) == QtCore.Qt.Checked:
                criterion.forbidden_tag__ids.add(tag._id)
        criterion.active_tags = set(self.tag_for_node_item.values())
        return criterion
    
