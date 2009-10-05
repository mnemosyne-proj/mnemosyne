#
# activate_cards_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.card_set_name_dlg import CardSetNameDlg
from mnemosyne.pyqt_ui.ui_activate_cards_dlg import Ui_ActivateCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog
from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
     DefaultCriterion


class ActivateCardsDlg(QtGui.QDialog, Ui_ActivateCardsDlg,
                       ActivateCardsDialog):

    """Note that this dialog can support active tags and forbidden tags,
    but not at the same time, in order to keep the interface compact.

    """

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
        # Initialise widgets.
        self.saved_sets.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self.saved_sets,
                     QtCore.SIGNAL("customContextMenuRequested(QPoint)"),
                     self.saved_sets_custom_menu)
        self.update_saved_sets_pane()
        criterion = self.database().current_activity_criterion()
        self.update_criterion_pane(criterion)
        # Finalise.
        self.tags_tree.sortItems(0, QtCore.Qt.AscendingOrder)
        self.tags_tree.expandAll()

    def activate(self):
        self.exec_()

    def update_saved_sets_pane(self):
        self.saved_sets.clear()
        self.criteria_by_name = {}
        active_name = ""
        active_criterion = self.database().current_activity_criterion()
        for criterion in self.database().get_activity_criteria():
            if criterion._id != 1:
                self.criteria_by_name[criterion.name] = criterion
                self.saved_sets.addItem(criterion.name)
                if criterion.criterion_type \
                       == active_criterion.criterion_type \
                   and criterion.data_to_string() \
                   == active_criterion.data_to_string():
                    active_name = criterion.name
        self.saved_sets.sortItems()
        if active_name:
            item = self.saved_sets.findItems(active_name,
                QtCore.Qt.MatchExactly)[0]
            self.saved_sets.setCurrentItem(item)        
        splitter_sizes = self.splitter.sizes()
        if self.saved_sets.count() == 0:
            self.splitter.setSizes([0, sum(splitter_sizes)])
        else:
            if splitter_sizes[0] == 0:
                self.splitter.setSizes([100, sum(splitter_sizes)-100])
            
    def update_criterion_pane(self, criterion):
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
        for tag in self.database().get_tags():
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
        elif len(criterion.active_tag__ids):
            self.active_or_forbidden.setCurrentIndex(0)
            for node_item, tag in self.tag_for_node_item.iteritems():
                if tag._id in criterion.active_tag__ids:
                    node_item.setCheckState(0, QtCore.Qt.Checked)
                else:
                    node_item.setCheckState(0, QtCore.Qt.Unchecked)
        self.tags_tree.expandAll()

    def saved_sets_custom_menu(self, pos):
        menu = QtGui.QMenu()
        menu.addAction(_("Delete"), self.delete_set)
        menu.addAction(_("Rename"), self.rename_set)
        menu.exec_(self.saved_sets.mapToGlobal(pos))

    def delete_set(self):
        answer = self.main_widget().question_box(_("Delete this set?"),
            _("&OK"), _("&Cancel"), "")
        if answer == 1:  # Cancel.
            return -1
        else:
            name = unicode(self.saved_sets.currentItem().text())
            criterion = self.criteria_by_name[name]
            self.database().delete_activity_criterion(criterion)
            self.database().save()
            self.update_saved_sets_pane()

    def rename_set(self):
        name = unicode(self.saved_sets.currentItem().text())
        criterion = self.criteria_by_name[name]
        forbidden_names = self.criteria_by_name.keys()
        forbidden_names.remove(name)
        CardSetNameDlg(self.component_manager, criterion,
                       forbidden_names).exec_()
        if not criterion.name:  # User cancelled.
            criterion.name = name
            return
        self.database().update_activity_criterion(criterion)
        self.database().save()
        self.update_saved_sets_pane()
        item = self.saved_sets.findItems(criterion.name,
            QtCore.Qt.MatchExactly)[0]
        self.saved_sets.setCurrentItem(item)
        
    def entered_criterion(self):

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

    def entered_criterion_changed(self):
        
        """Called whenever the user updates the criterion information in the
        lower pane (not when loading a new criterion by clicking one in the
        upper pane.

        """

    def load_set(self, item):
        name = unicode(item.text())
        criterion = self.criteria_by_name[name]
        self.update_criterion_pane(criterion)
            
    def store_layout(self):
        self.config()["activate_cards_dlg_size"] = \
            (self.width(), self.height())
        self.config()["activate_cards_dlg_splitter"] = \
            self.splitter.sizes()
        
    def closeEvent(self, event):
        self.store_layout()
        
    def accept(self):
        self.database().set_current_activity_criterion(\
            self.entered_criterion())
        self.store_layout()
        return QtGui.QDialog.accept(self)

    def save(self):
        criterion = self.entered_criterion()
        CardSetNameDlg(self.component_manager, criterion,
                       self.criteria_by_name.keys()).exec_()
        if not criterion.name:  # User cancelled.
            return
        self.database().add_activity_criterion(criterion)
        self.update_saved_sets_pane()
        item = self.saved_sets.findItems(criterion.name,
            QtCore.Qt.MatchExactly)[0]
        self.saved_sets.setCurrentItem(item)
        
    def reject(self):
        self.store_layout()
        QtGui.QDialog.reject(self)
