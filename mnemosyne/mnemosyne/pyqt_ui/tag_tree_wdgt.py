#
# tag_tree_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.tag_tree import TagTree
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion

# We hijack QTreeWidgetItem a bit and store extra data in hidden columns, so
# that we don't need to implement a custom tree model.

DISPLAY_STRING = 0
EDIT_STRING = 1
NODE = 2

class TagDelegate(QtGui.QStyledItemDelegate):

    tree_rebuild_needed = QtCore.pyqtSignal()   

    def __init__(self, component_manager, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        editor = QtGui.QStyledItemDelegate.createEditor\
            (self, parent, option, index)
        editor.returnPressed.connect(self.commit_and_close_editor)
        return editor

    def setEditorData(self, editor, index):
        edit_index = index.model().index(index.row(), EDIT_STRING, index.parent())        
        editor.setText(index.model().data(edit_index).toString())
        
    def commit_and_close_editor(self):
        editor = self.sender()
        self.closeEditor.emit(editor, QtGui.QAbstractItemDelegate.NoHint)
        # TODO: rename tags.
        self.tree_rebuild_needed.emit()

class TagsTreeWdgt(QtGui.QWidget, Component):

    """Displays all the tags in a tree together with check boxes."""

    def __init__(self, component_manager, parent):
        Component.__init__(self, component_manager)
        QtGui.QWidget.__init__(self, parent)
        self.layout = QtGui.QVBoxLayout(self)
        self.tag_tree_wdgt = QtGui.QTreeWidget(self)
        self.tag_tree_wdgt.setColumnCount(3)
        self.tag_tree_wdgt.setColumnHidden(1, True)
        self.tag_tree_wdgt.setColumnHidden(EDIT_STRING, True)
        self.tag_tree_wdgt.setColumnHidden(NODE, True)        
        self.tag_tree_wdgt.setHeaderHidden(True)
        self.delegate = TagDelegate(component_manager, self)
        self.tag_tree_wdgt.setItemDelegate(self.delegate)
        self.delegate.tree_rebuild_needed.connect(self.display)
        self.layout.addWidget(self.tag_tree_wdgt)

    def create_tree(self, tree, qt_parent):

        #rename_tag_action = QAction(_("Rename tag"), pContextMenu);
        #pTreeWidget->setContextMenuPolicy(Qt::ActionsContextMenu);
        #pTreeWidget->addAction(pTestCard);
        
        for node in tree:
            node_name = "%s (%d)" % \
                (self.tag_tree.display_name_for_node[node],
                self.tag_tree.card_count_for_node[node])
            node_item = QtGui.QTreeWidgetItem(qt_parent,
                [node_name, "", node], 0)
            node_item.setFlags(node_item.flags() | \
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
            if node not in ["__ALL__", "__UNTAGGED__"]:
                node_item.setFlags(node_item.flags() | \
                    QtCore.Qt.ItemIsEditable)
            # For nodes which correspond to a tag, we show the full
            # tag name (i.e. all levels including ::), otherwise we
            # cannot change the hierarchy of the tag.
            # For internal nodes, we only show the name corresponding to
            # that level.
            if node in self._tag_names:
                self.tag_for_node_item[node_item] = \
                    self.database().get_or_create_tag_with_name(node)
                node_item.setData(EDIT_STRING, QtCore.Qt.DisplayRole,
                    QtCore.QVariant(QtCore.QString(node)))
            else:
                node_item.setData(EDIT_STRING, QtCore.Qt.DisplayRole,
                    QtCore.QVariant(QtCore.QString(\
                    self.tag_tree.display_name_for_node[node])))                
            self.create_tree(tree=self.tag_tree[node], qt_parent=node_item)
        
    def display(self, criterion=None):
        # Create criterion if needed.
        if criterion is None:
            criterion = DefaultCriterion(self.component_manager)
            for tag in self.database().tags():
                criterion.active_tag__ids.add(tag._id)            
        # Create tree.
        self.tag_tree_wdgt.clear()
        self.tag_for_node_item = {}
        self._tag_names = [tag.name for tag in self.database().tags()]
        self.tag_tree = TagTree(self.component_manager)
        node = "__ALL__"
        node_name = "%s (%d)" % (self.tag_tree.display_name_for_node[node],
            self.tag_tree.card_count_for_node[node])
        root = self.tag_tree[node]
        root_item = QtGui.QTreeWidgetItem(self.tag_tree_wdgt, [node_name], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
        root_item.setCheckState(0, QtCore.Qt.Checked)
        self.create_tree(self.tag_tree[node], qt_parent=root_item)            
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
    
