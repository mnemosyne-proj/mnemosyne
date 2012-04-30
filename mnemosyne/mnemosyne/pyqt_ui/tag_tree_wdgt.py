#
# tag_tree_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.tag_tree import TagTree
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion

# We hijack QTreeWidgetItem a bit and store extra data in a hidden column, so
# that we don't need to implement a custom tree model.
# The first column stores the string displayed, i.e. the leaf part of the
# hierachical tag name. The second column stores the node id, i.e. the
# full tag name.

DISPLAY_STRING = 0
NODE = 1

class TagDelegate(QtGui.QStyledItemDelegate):

    rename_node = QtCore.pyqtSignal(unicode, unicode)
    redraw_node = QtCore.pyqtSignal(unicode)

    def __init__(self, component_manager, parent=None):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.previous_node_name = None

    def createEditor(self, parent, option, index):

        # Ideally, we want to capture the focusOut event here, to redraw the
        # card counts in case of an aborted edit by the user. One option to
        # achieve this is connecting the editingFinished signal instead of
        # returnPressed, but there is a long-standing bug in Qt causing this
        # signal to be emitted twice, with the second call sometimes coming
        # when the first one has not finished yet, which can cause crashes.
        # The other option is to reimplement focusOutEvent of the editor, but
        # that does not seem to work here easily in the context of Delegates.
        # Presumably subclassing QLineEdit would work, though, but at the cost
        # of added complexity.
        #
        # See also:
        #
        #  http://www.qtforum.org/article/33631/qlineedit-the-signal-editingfinished-is-emitted-twice.html
        #  http://bugreports.qt.nokia.com/browse/QTBUG-40

        editor = QtGui.QStyledItemDelegate.createEditor\
            (self, parent, option, index)
        editor.returnPressed.connect(self.commit_and_close_editor)
        return editor

    def setEditorData(self, editor, index):
        # We display the full node (i.e. all levels including ::), so that
        # the hierarchy can be changed upon editing.
        node_index = index.model().index(index.row(), NODE, index.parent())
        self.previous_node_name = index.model().data(node_index).toString()
        editor.setText(self.previous_node_name)

    def commit_and_close_editor(self):
        editor = self.sender()
        if unicode(self.previous_node_name) == unicode(editor.text()):
            self.redraw_node.emit(self.previous_node_name)
        else:
            self.rename_node.emit(self.previous_node_name, editor.text())
        self.closeEditor.emit(editor, QtGui.QAbstractItemDelegate.NoHint)


class TagsTreeWdgt(QtGui.QWidget, Component):

    """Displays all the tags in a tree together with check boxes.

    If 'before_using_libmnemosyne_db_hook' and 'after_using_libmnemosyne_db'
    are set, these will be called before and after using libmnemosyne
    operations which can modify the database.

    Typical use case for this comes from a parent widget like the card
    browser, which needs to relinquish its control over the sqlite database
    first, before the tag tree operations can take place.

    """

    def __init__(self, component_manager, parent,
            before_using_libmnemosyne_db_hook=None,
            after_using_libmnemosyne_db_hook=None):
        Component.__init__(self, component_manager)
        QtGui.QWidget.__init__(self, parent)
        self.before_using_libmnemosyne_db_hook = \
            before_using_libmnemosyne_db_hook
        self.after_using_libmnemosyne_db_hook = \
            after_using_libmnemosyne_db_hook
        self.layout = QtGui.QVBoxLayout(self)
        self.tree_wdgt = QtGui.QTreeWidget(self)
        self.tree_wdgt.setColumnCount(2)
        self.tree_wdgt.setColumnHidden(1, True)
        self.tree_wdgt.setColumnHidden(NODE, True)
        self.tree_wdgt.setHeaderHidden(True)
        self.tree_wdgt.setSelectionMode(\
            QtGui.QAbstractItemView.ExtendedSelection)
        self.delegate = TagDelegate(component_manager, self)
        self.tree_wdgt.setItemDelegate(self.delegate)
        self.delegate.rename_node.connect(self.rename_node)
        self.delegate.redraw_node.connect(self.redraw_node)
        self.layout.addWidget(self.tree_wdgt)
        self.tree_wdgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_wdgt.customContextMenuRequested.connect(\
            self.context_menu)

    def selected_nodes_which_can_be_renamed(self):
        nodes = []
        for index in self.tree_wdgt.selectedIndexes():
            node_index = \
                index.model().index(index.row(), NODE, index.parent())
            node = index.model().data(node_index).toString()
            if node in self.nodes_which_can_be_renamed:
                nodes.append(node)
        return nodes

    def selected_nodes_which_can_be_deleted(self):
        nodes = []
        for index in self.tree_wdgt.selectedIndexes():
            node_index = \
                index.model().index(index.row(), NODE, index.parent())
            node = index.model().data(node_index).toString()
            if node in self.nodes_which_can_be_deleted:
                nodes.append(node)
        return nodes

    def context_menu(self, point):
        menu = QtGui.QMenu(self)
        to_rename = self.selected_nodes_which_can_be_renamed()
        if len(to_rename) >= 1:
            rename_action = QtGui.QAction(_("&Rename"), menu)
            rename_action.triggered.connect(self.menu_rename)
            rename_action.setShortcut(QtCore.Qt.Key_Enter)
            menu.addAction(rename_action)
            if len(to_rename) > 1:
                rename_action.setEnabled(False)
        to_delete = self.selected_nodes_which_can_be_deleted()
        if len(to_delete) >= 1:
            delete_action = QtGui.QAction(_("&Delete"), menu)
            delete_action.triggered.connect(self.menu_delete)
            delete_action.setShortcut(QtGui.QKeySequence.Delete)
            menu.addAction(delete_action)
        if len(to_delete) + len(to_rename) >= 1:
            menu.exec_(self.tree_wdgt.mapToGlobal(point))

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.menu_rename()
        elif event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            self.menu_delete()

    def menu_rename(self):
        nodes = self.selected_nodes_which_can_be_renamed()
        # If there are tags selected, this means that we could only have got
        # after pressing return on an actual edit, due to our custom
        # 'keyPressEvent'. We should not continue in that case.
        if len(nodes) == 0:
            return
        # We display the full node (i.e. all levels including ::), so that
        # the hierarchy can be changed upon editing.

        from mnemosyne.pyqt_ui.ui_rename_tag_dlg import Ui_RenameTagDlg

        class RenameDlg(QtGui.QDialog, Ui_RenameTagDlg):
            def __init__(self, old_tag_name):
                QtGui.QDialog.__init__(self)
                self.setupUi(self)
                self.tag_name.setText(old_tag_name)

        old_tag_name = nodes[0]
        dlg = RenameDlg(old_tag_name)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self.rename_node(nodes[0], unicode(dlg.tag_name.text()))

    def menu_delete(self):
        nodes = self.selected_nodes_which_can_be_deleted()
        if len(nodes) == 0:
            return
        if len(nodes) > 1:
            question = _("Delete these tags? Cards with these tags will not be deleted.")
        else:
            question = _("Delete this tag? Cards with this tag will not be deleted.")
        answer = self.main_widget().show_question\
            (question, _("&OK"), _("&Cancel"), "")
        if answer == 1: # Cancel.
            return
        self.delete_nodes(nodes)

    def create_tree(self, tree, qt_parent):
        for node in tree:
            node_name = "%s (%d)" % \
                (self.tag_tree.display_name_for_node[node],
                self.tag_tree.card_count_for_node[node])
            node_item = QtGui.QTreeWidgetItem(qt_parent, [node_name, node], 0)
            node_item.setFlags(node_item.flags() | \
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
            if node not in ["__ALL__", "__UNTAGGED__"]:
                node_item.setFlags(node_item.flags() | \
                    QtCore.Qt.ItemIsEditable)
                self.nodes_which_can_be_renamed.append(node)
                self.nodes_which_can_be_deleted.append(node)
            if node in self.tag_tree.tag_for_node:
                self.tag_for_node_item[node_item] = \
                    self.tag_tree.tag_for_node[node]
            node_item.setData(NODE, QtCore.Qt.DisplayRole,
                    QtCore.QVariant(QtCore.QString(node)))
            self.create_tree(tree=self.tag_tree[node], qt_parent=node_item)

    def display(self, criterion=None):
        # Create criterion if needed.
        if criterion is None:
            criterion = DefaultCriterion(self.component_manager)
            for tag in self.database().tags():
                criterion._tag_ids_active.add(tag._id)
        # Create tree.
        self.tag_tree = TagTree(self.component_manager)
        self.tree_wdgt.clear()
        self.tag_for_node_item = {}
        self.nodes_which_can_be_deleted = []
        self.nodes_which_can_be_renamed = []
        node = "__ALL__"
        node_name = "%s (%d)" % (self.tag_tree.display_name_for_node[node],
            self.tag_tree.card_count_for_node[node])
        root = self.tag_tree[node]
        root_item = QtGui.QTreeWidgetItem(\
            self.tree_wdgt, [node_name, node], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsTristate)
        root_item.setCheckState(0, QtCore.Qt.Checked)
        self.create_tree(self.tag_tree[node], qt_parent=root_item)
        # Set forbidden tags.
        if len(criterion._tag_ids_forbidden):
            for node_item, tag in self.tag_for_node_item.iteritems():
                if tag._id in criterion._tag_ids_forbidden:
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.Unchecked)
        # Set active tags.
        else:
            for node_item, tag in self.tag_for_node_item.iteritems():
                if tag._id in criterion._tag_ids_active:
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.Unchecked)
        # Finalise.
        self.tree_wdgt.expandAll()

    def checked_to_active_tags_in_criterion(self, criterion):
        for item, tag in self.tag_for_node_item.iteritems():
            if item.checkState(0) == QtCore.Qt.Checked:
                criterion._tag_ids_active.add(tag._id)
        criterion.forbidden_tags = set()
        return criterion

    def checked_to_forbidden_tags_in_criterion(self, criterion):
        for item, tag in self.tag_for_node_item.iteritems():
            if item.checkState(0) == QtCore.Qt.Checked:
                criterion._tag_ids_forbidden.add(tag._id)
        criterion.active_tags = set(self.tag_for_node_item.values())
        return criterion

    def save_criterion(self):
        self.saved_criterion = DefaultCriterion(self.component_manager)
        self.checked_to_active_tags_in_criterion(self.saved_criterion)
        # Now we've saved the checked state of the tree.
        # Saving and restoring the selected state is less trivial, because
        # in the case of trees, the model indexes have parents which become
        # invalid when creating the widget.
        # The solution would be to save tags and reselect those in the new
        # widget.

    def restore_criterion(self):
        new_criterion = DefaultCriterion(self.component_manager)
        for tag in self.database().tags():
            if tag._id in self.saved_criterion._tag_ids_active:
                new_criterion._tag_ids_active.add(tag._id)
        self.display(new_criterion)

    def hibernate(self):

        """Save the current criterion and unload the database so that
        we can call libmnemosyne functions.

        """

        self.save_criterion()
        if self.before_using_libmnemosyne_db_hook:
            self.before_using_libmnemosyne_db_hook()

    def wakeup(self):

        """Restore the saved criterion and reload the database after
        calling libmnemosyne functions.

        """

        self.restore_criterion()
        if self.after_using_libmnemosyne_db_hook:
            self.after_using_libmnemosyne_db_hook()

    def rename_node(self, node, new_name):
        self.hibernate()
        self.tag_tree.rename_node(unicode(node), unicode(new_name))
        self.wakeup()

    def delete_nodes(self, nodes):
        self.hibernate()
        for node in nodes:
            self.tag_tree.delete_subtree(unicode(node))
        self.wakeup()

    def redraw_node(self, node):

        """When renaming a tag to the same name, we need to redraw the node
        to show the card count again.

        """

        # We do the redrawing in a rather hackish way now, simply by
        # recreating the widget. Could be sped up, but at the expense of more
        # complicated code.
        self.save_criterion()
        self.restore_criterion()

    def rebuild(self):

        """To be called when external events invalidate the tag tree,
        e.g. due to edits in the card browser widget.

        """

        self.hibernate()
        self.tag_tree = TagTree(self.component_manager)
        self.wakeup()
