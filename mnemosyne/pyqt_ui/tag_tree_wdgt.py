#
# tag_tree_wdgt.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
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

class TagDelegate(QtWidgets.QStyledItemDelegate):

    rename_node = QtCore.pyqtSignal(str, str)
    redraw_node = QtCore.pyqtSignal(str)

    def __init__(self, component_manager, **kwds):
        super().__init__(**kwds)
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
        #  https://bugreports.qt-project.org/browse/QTBUG-40

        editor = QtWidgets.QStyledItemDelegate.createEditor\
            (self, parent, option, index)
        editor.returnPressed.connect(self.commit_and_close_editor)
        return editor

    def setEditorData(self, editor, index):
        # We display the full node (i.e. all levels including ::), so that
        # the hierarchy can be changed upon editing.
        node_index = index.model().index(index.row(), NODE, index.parent())
        self.previous_node_name = index.model().data(node_index).\
            replace("::" + _("Untagged"), "" )
        editor.setText(self.previous_node_name)

    def commit_and_close_editor(self):
        editor = self.sender()
        if self.previous_node_name == editor.text():
            self.redraw_node.emit(self.previous_node_name)
        else:
            self.rename_node.emit(self.previous_node_name, editor.text())
        self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.EndEditHint.NoHint)


class TagsTreeWdgt(Component, QtWidgets.QWidget):

    """Displays all the tags in a tree together with check boxes. """

    tags_changed_signal = QtCore.pyqtSignal()

    def __init__(self, acquire_database=None, **kwds):
        super().__init__(**kwds)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.tree_wdgt = QtWidgets.QTreeWidget(self)
        self.tree_wdgt.setColumnCount(2)
        self.tree_wdgt.setColumnHidden(1, True)
        self.tree_wdgt.setColumnHidden(NODE, True)
        self.tree_wdgt.setHeaderHidden(True)
        self.tree_wdgt.setSelectionMode(\
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.delegate = TagDelegate(\
            component_manager=kwds["component_manager"], parent=self)
        self.tree_wdgt.setItemDelegate(self.delegate)
        self.delegate.rename_node.connect(self.rename_node)
        self.delegate.redraw_node.connect(self.redraw_node)
        self.layout.addWidget(self.tree_wdgt)
        self.tree_wdgt.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_wdgt.customContextMenuRequested.connect(\
            self.context_menu)
        self.acquire_database = acquire_database

    def selected_nodes_which_can_be_renamed(self):
        nodes = []
        for index in self.tree_wdgt.selectedIndexes():
            node_index = \
                index.model().index(index.row(), NODE, index.parent())
            node = index.model().data(node_index)
            if node in self.nodes_which_can_be_renamed:
                nodes.append(node)
        return nodes

    def selected_nodes_which_can_be_deleted(self):
        nodes = []
        for index in self.tree_wdgt.selectedIndexes():
            node_index = \
                index.model().index(index.row(), NODE, index.parent())
            node = index.model().data(node_index)
            if node in self.nodes_which_can_be_deleted:
                nodes.append(node)
        return nodes

    def context_menu(self, point):
        menu = QtWidgets.QMenu(self)
        to_rename = self.selected_nodes_which_can_be_renamed()
        if len(to_rename) >= 1:
            rename_action = QtGui.QAction(_("&Rename"), menu)
            rename_action.triggered.connect(self.menu_rename)
            rename_action.setShortcut(QtCore.Qt.Key.Key_Enter)
            menu.addAction(rename_action)
            if len(to_rename) > 1:
                rename_action.setEnabled(False)
        to_delete = self.selected_nodes_which_can_be_deleted()
        if len(to_delete) >= 1:
            delete_action = QtGui.QAction(_("&Delete"), menu)
            delete_action.triggered.connect(self.menu_delete)
            delete_action.setShortcut(QtGui.QKeySequence.StandardKey.Delete)
            menu.addAction(delete_action)
        if len(to_delete) + len(to_rename) >= 1:
            menu.exec(self.tree_wdgt.mapToGlobal(point))

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return]:
            self.menu_rename()
        elif event.key() in [QtCore.Qt.Key.Key_Delete, QtCore.Qt.Key.Key_Backspace]:
            self.menu_delete()
        else:
            QtWidgets.QWidget.keyPressEvent(self, event)

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

        class RenameDlg(QtWidgets.QDialog, Ui_RenameTagDlg):
            def __init__(self, old_tag_name):
                super().__init__()
                self.setupUi(self)
                self.tag_name.setText(\
                    old_tag_name.replace("::" + _("Untagged"), "" ))

        old_tag_name = nodes[0]
        dlg = RenameDlg(old_tag_name)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.rename_node(nodes[0], dlg.tag_name.text())

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
            node_item = QtWidgets.QTreeWidgetItem(qt_parent, [node_name, node], 0)
            node_item.setFlags(node_item.flags() | \
                QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsAutoTristate)
            if node not in ["__ALL__", "__UNTAGGED__"] and \
                not "::" + _("Untagged") in node:
                node_item.setFlags(node_item.flags() | \
                    QtCore.Qt.ItemFlag.ItemIsEditable)
                self.nodes_which_can_be_renamed.append(node)
                self.nodes_which_can_be_deleted.append(node)
            if node in self.tag_tree.tag_for_node:
                # Since node_item seems mutable, we cannot use a dict.
                self.node_items.append(node_item)
                self.tag_for_node_item.append(self.tag_tree.tag_for_node[node])
            node_item.setData(NODE, QtCore.Qt.ItemDataRole.DisplayRole,
                    QtCore.QVariant(node))
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
        self.node_items = []
        self.tag_for_node_item = []
        self.nodes_which_can_be_deleted = []
        self.nodes_which_can_be_renamed = []
        node = "__ALL__"
        node_name = "%s (%d)" % (self.tag_tree.display_name_for_node[node],
            self.tag_tree.card_count_for_node[node])
        root = self.tag_tree[node]
        root_item = QtWidgets.QTreeWidgetItem(\
            self.tree_wdgt, [node_name, node], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsAutoTristate)
        root_item.setCheckState(0, QtCore.Qt.CheckState.Checked)
        self.create_tree(self.tag_tree[node], qt_parent=root_item)
        # Set forbidden tags.
        if len(criterion._tag_ids_forbidden):
            for i in range(len(self.node_items)):
                node_item = self.node_items[i]
                tag = self.tag_for_node_item[i]
                if tag._id in criterion._tag_ids_forbidden:
                    node_item.setCheckState(0, QtCore.Qt.CheckState.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
        # Set active tags.
        else:
            # We first set all the tags inactive. We cannot do this in the
            # second branch of the upcoming 'if' statement, as then an
            # inactive parent tag coming later in the list will deactivate
            # active child tags coming earlier in the list.
            for node_item in self.node_items:
                node_item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)
            for i in range(len(self.node_items)):
                node_item = self.node_items[i]
                tag = self.tag_for_node_item[i]
                if tag._id in criterion._tag_ids_active:
                    node_item.setCheckState(0, QtCore.Qt.CheckState.Checked)
        # Restore state of the tree.
        self.tree_wdgt.expandAll()
        collapsed = self.config()["tag_tree_wdgt_state"]
        if collapsed is None:
            collapsed = []
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_wdgt)
        while iterator.value():
            if iterator.value().text(1) in collapsed:
                iterator.value().setExpanded(False)
            iterator += 1

    def checked_to_active_tags_in_criterion(self, criterion):
        for i in range(len(self.node_items)):
            tag = self.tag_for_node_item[i]
            if self.node_items[i].checkState(0) == QtCore.Qt.CheckState.Checked:
                criterion._tag_ids_active.add(tag._id)
        criterion._tag_ids_forbidden = set()
        return criterion

    def checked_to_forbidden_tags_in_criterion(self, criterion):
        for i in range(len(self.node_items)):
            tag = self.tag_for_node_item[i]
            if self.node_items[i].checkState(0) == QtCore.Qt.CheckState.Checked:
                criterion._tag_ids_forbidden.add(tag._id)
        criterion._tag_ids_active = \
            set([tag._id for tag in self.tag_for_node_item])
        return criterion

    def unchecked_to_forbidden_tags_in_criterion(self, criterion):
        for i in range(len(self.node_items)):
            tag = self.tag_for_node_item[i]
            if self.node_items[i].checkState(0) == QtCore.Qt.CheckState.Unchecked:
                criterion._tag_ids_forbidden.add(tag._id)
        return criterion

    def save_criterion(self):
        self.saved_criterion = DefaultCriterion(self.component_manager)
        self.checked_to_active_tags_in_criterion(self.saved_criterion)
        # We also save the unchecked tags as this will allow us to identify
        # any new tags created afterwards.
        self.unchecked_to_forbidden_tags_in_criterion(self.saved_criterion)
        # Now we've saved the checked state of the tree.
        # Saving and restoring the selected state is less trivial, because
        # in the case of trees, the model indexes have parents which become
        # invalid when creating the widget.
        # The solution would be to save tags and reselect those in the new
        # widget.

    def restore_criterion(self):
        new_criterion = DefaultCriterion(self.component_manager)
        for tag in self.database().tags():
            if tag._id in self.saved_criterion._tag_ids_active or \
               tag._id not in self.saved_criterion._tag_ids_forbidden:
               # Second case deals with recently added tag.
                new_criterion._tag_ids_active.add(tag._id)
        self.display(new_criterion)

    def store_tree_state(self):

        """Store which nodes are collapsed. """

        collapsed = []
        iterator = QtWidgets.QTreeWidgetItemIterator(self.tree_wdgt)
        while iterator.value():
            if not iterator.value().isExpanded():
                collapsed.append(iterator.value().text(1))
            iterator += 1
        self.config()["tag_tree_wdgt_state"] = collapsed

    def rename_node(self, node, new_name):
        if self.acquire_database:
            self.acquire_database()
        self.save_criterion()
        self.store_tree_state()
        self.tag_tree.rename_node(node, new_name)
        self.restore_criterion()
        self.tags_changed_signal.emit()

    def delete_nodes(self, nodes):
        if self.acquire_database:
            self.acquire_database()
        self.save_criterion()
        self.store_tree_state()
        for node in nodes:
            self.tag_tree.delete_subtree(node)
        self.restore_criterion()
        self.tags_changed_signal.emit()

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

        self.save_criterion()
        self.store_tree_state()
        self.tag_tree = TagTree(self.component_manager)
        self.restore_criterion()

    def closeEvent(self, event):
        self.store_tree_state()
