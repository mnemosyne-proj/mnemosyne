#
# card_type_tree_wdgt.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion

# Code reuse through inheritance.
from mnemosyne.pyqt_ui.tag_tree_wdgt import TagDelegate, TagsTreeWdgt

# We hijack QTreeWidgetItem a bit and store extra data in a hidden column, so
# that we don't need to implement a custom tree model.
# The first column stores the string displayed, i.e. the card type id.
# For card types, the second column stores the node id, in this case
# the card type id.

DISPLAY_STRING = 0
NODE = 1

class CardTypeDelegate(TagDelegate):

    def setEditorData(self, editor, index):
        # Get rid of the card count.
        self.previous_node_name = \
            index.model().data(index).rsplit(" (", 1)[0]
        node_index = index.model().index(index.row(), NODE, index.parent())
        self.card_type_id = index.model().data(node_index)
        editor.setText(self.previous_node_name)

    def commit_and_close_editor(self):
        editor = self.sender()
        if self.previous_node_name == editor.text():
            self.redraw_node.emit(self.card_type_id)
        else:
            self.rename_node.emit(self.card_type_id, editor.text())
        self.closeEditor.emit(editor, QtWidgets.QAbstractItemDelegate.EndEditHint.NoHint)


class CardTypesTreeWdgt(TagsTreeWdgt):

    """Displays all the card types in a tree together with check boxes."""

    card_types_changed_signal = QtCore.pyqtSignal()

    def __init__(self, acquire_database=None, **kwds):
        super().__init__(**kwds)
        self.delegate = CardTypeDelegate(\
            component_manager=kwds["component_manager"], parent=self)
        self.tree_wdgt.setItemDelegate(self.delegate)
        self.delegate.rename_node.connect(self.rename_node)
        self.delegate.redraw_node.connect(self.redraw_node)
        self.acquire_database = acquire_database

    def menu_rename(self):
        nodes = self.selected_nodes_which_can_be_renamed()
        # If there are tags selected, this means that we could only have got
        # after pressing return on an actual edit, due to our custom
        # 'keyPressEvent'. We should not continue in that case.
        if len(nodes) == 0:
            return

        from mnemosyne.pyqt_ui.ui_rename_card_type_dlg \
            import Ui_RenameCardTypeDlg

        class RenameDlg(QtWidgets.QDialog, Ui_RenameCardTypeDlg):
            def __init__(self, old_card_type_name):
                super().__init__()
                self.setupUi(self)
                self.card_type_name.setText(old_card_type_name)

        old_card_type_name = self.card_type_with_id(nodes[0]).name
        dlg = RenameDlg(old_card_type_name)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.rename_node(nodes[0], dlg.card_type_name.text())

    def menu_delete(self):
        nodes = self.selected_nodes_which_can_be_deleted()
        if len(nodes) == 0:
            return
        if len(nodes) > 1:
            question = _("Delete these card types?")
        else:
            question = _("Delete this card type?")
        answer = self.main_widget().show_question\
            (question, _("&OK"), _("&Cancel"), "")
        if answer == 1: # Cancel.
            return
        self.delete_nodes(nodes)

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
                count = self.database().card_count_for_fact_view \
                    (fact_view, active_only=False)
                card_type_count += count
                count_for_fact_view[fact_view] = count
            count_for_card_type[card_type] = card_type_count
            root_count += card_type_count
        # Fill widget.
        self.nodes_which_can_be_deleted = []
        self.nodes_which_can_be_renamed = []
        self.tree_wdgt.clear()
        self.node_items = []
        self.card_type_fact_view_ids_for_node_item = []
        root_item = QtWidgets.QTreeWidgetItem(self.tree_wdgt,
            [_("All card types (%d)") % root_count], 0)
        root_item.setFlags(root_item.flags() | \
           QtCore.Qt.ItemFlag.ItemIsUserCheckable | \
           QtCore.Qt.ItemFlag.ItemIsAutoTristate)
        root_item.setCheckState(0, QtCore.Qt.CheckState.Checked)
        for card_type in self.database().sorted_card_types():
            if card_type.hidden_from_UI:
                continue
            card_type_item = QtWidgets.QTreeWidgetItem(root_item, ["%s (%d)" % \
                (_(card_type.name), count_for_card_type[card_type])], 0)
            card_type_item.setFlags(card_type_item.flags() | \
                QtCore.Qt.ItemFlag.ItemIsUserCheckable | QtCore.Qt.ItemFlag.ItemIsAutoTristate)
            card_type_item.setCheckState(0, QtCore.Qt.CheckState.Checked)
            card_type_item.setData(NODE, QtCore.Qt.ItemDataRole.DisplayRole,
                    QtCore.QVariant(card_type.id))
            if count_for_card_type[card_type] == 0 and \
                self.database().is_user_card_type(card_type):
                    self.nodes_which_can_be_deleted.append(card_type.id)
            if self.database().is_user_card_type(card_type):
                self.nodes_which_can_be_renamed.append(card_type.id)
                card_type_item.setFlags(card_type_item.flags() | \
                    QtCore.Qt.ItemFlag.ItemIsEditable)
            for fact_view in card_type.fact_views:
                fact_view_item = QtWidgets.QTreeWidgetItem(card_type_item,
                    ["%s (%d)" % (_(fact_view.name),
                    count_for_fact_view[fact_view])], 0)
                fact_view_item.setFlags(fact_view_item.flags() | \
                    QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                if (card_type.id, fact_view.id) in \
                    criterion.deactivated_card_type_fact_view_ids:
                    check_state = QtCore.Qt.CheckState.Unchecked
                else:
                    check_state = QtCore.Qt.CheckState.Checked
                fact_view_item.setCheckState(0, check_state)
                # Since fact_view_item seems mutable, we cannot use a dict.
                self.node_items.append(fact_view_item)
                self.card_type_fact_view_ids_for_node_item.append(\
                    (card_type.id, fact_view.id))
        self.tree_wdgt.expandAll()

    def checked_to_criterion(self, criterion):
        criterion.deactivated_card_type_fact_view_ids = set()
        for i in range(len(self.node_items)):
            item = self.node_items[i]
            card_type_fact_view_ids = \
                self.card_type_fact_view_ids_for_node_item[i]
            if item.checkState(0) == QtCore.Qt.CheckState.Unchecked:
                criterion.deactivated_card_type_fact_view_ids.add(\
                    card_type_fact_view_ids)
        return criterion

    def save_criterion(self):
        self.saved_criterion = DefaultCriterion(self.component_manager)
        self.checked_to_criterion(self.saved_criterion)
        # Now we've saved the checked state of the tree.
        # Saving and restoring the selected state is less trivial, because
        # in the case of trees, the model indexes have parents which become
        # invalid when creating the widget.
        # The solution would be to save tags and reselect those in the new
        # widget.

    def restore_criterion(self):
        # See if any card types have been deleted meanwhile.
        old_card_type_ids = set([cursor[0] for cursor in \
            self.saved_criterion.deactivated_card_type_fact_view_ids])
        deleted_card_type_ids = set()
        for card_type_id in old_card_type_ids:
            try:
                card_type = self.card_type_with_id(card_type_id)
            except:
                deleted_card_type_ids.add(card_type_id)
        # Remove offending entries.
        deactivated_card_type_fact_view_ids = \
            self.saved_criterion.deactivated_card_type_fact_view_ids
        for card_type_id, fact_view_id in deactivated_card_type_fact_view_ids:
            if card_type_id in deleted_card_type_ids:
                self.saved_criterion.deactivated_card_type_fact_view_ids.\
                    discard((card_type_id, fact_view_id))
        self.display(self.saved_criterion)

    def rename_node(self, node, new_name):
        if self.acquire_database:
            self.acquire_database()
        self.save_criterion()
        card_type = self.card_type_with_id(node)
        self.controller().rename_card_type(card_type, new_name)
        self.restore_criterion()
        self.card_types_changed_signal.emit()

    def delete_nodes(self, nodes):
        if self.acquire_database:
            self.acquire_database()
        self.save_criterion()
        for node in nodes:
            card_type = self.card_type_with_id(node)
            self.controller().delete_card_type(card_type)
        self.restore_criterion()
        self.card_types_changed_signal.emit()

    def rebuild(self):

        """To be called when external events invalidate the tag tree,
        e.g. due to edits in the card browser widget.

        """

        self.save_criterion()
        # Now we've saved the checked state of the tree.
        # Saving and restoring the selected state is less trivial, because
        # in the case of trees, the model indexes have parents which become
        # invalid when creating the widget.
        # The solution would be to save card types and reselect those in the
        # new widget.
        self.restore_criterion()
