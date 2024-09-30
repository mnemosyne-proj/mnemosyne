#
# activate_cards_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.card_set_name_dlg import CardSetNameDlg
from mnemosyne.pyqt_ui.ui_activate_cards_dlg import Ui_ActivateCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog
from mnemosyne.pyqt_ui.tip_after_starting_n_times import \
     TipAfterStartingNTimes

class ActivateCardsDlg(QtWidgets.QDialog, ActivateCardsDialog,
                       TipAfterStartingNTimes, Ui_ActivateCardsDlg):

    started_n_times_counter = "started_activate_cards_n_times"
    tip_after_n_times = \
        {3 : _("If you find yourself selecting the same tags and card types many types, you can press the button 'Save this set for later use' to give it a name to select it more quickly later."),
         6 : _("Double-click on the name of a saved set to quickly activate it and close the dialog."),
         9 : _("You can right-click on the name of a saved set to rename or delete it."),
         12 : _("If you single-click the name of a saved set, modifications to the selected tags and card types are not saved to that set unless you press 'Save this set for later use' again. This allows you to make some quick-and-dirty temporary modifications.")}

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        # Initialise widgets.
        self.was_showing_a_saved_set = False
        self.is_shutting_down = False
        criterion = self.database().current_criterion()
        self.criterion_classes = \
            self.component_manager.all("criterion")
        current_criterion = self.database().current_criterion()
        self.widget_for_criterion_type = {}
        for criterion_class in self.criterion_classes:
            widget = self.component_manager.current\
                ("criterion_widget", used_for=criterion_class)\
                (component_manager=self.component_manager, parent=self)
            self.tab_widget.addTab(widget, criterion_class.criterion_type)
            self.widget_for_criterion_type[criterion_class.criterion_type] \
                = widget
        self.tab_widget.setCurrentWidget(self.widget_for_criterion_type\
                                         [current_criterion.criterion_type])
        self.tab_widget.tabBar().setVisible(self.tab_widget.count() > 1)
        self.tab_widget.currentWidget().display_criterion(current_criterion)
        # Restore state.
        state = self.config()["activate_cards_dlg_state"]
        if state:
            self.restoreGeometry(state)
        splitter_state = self.config()["activate_cards_dlg_splitter_state"]
        if not splitter_state:
            self.splitter.setSizes([100, 350])
        else:
            self.splitter.restoreState(splitter_state)
        # Should go last, otherwise the selection of the saved sets pane will
        # always be cleared.
        self.update_saved_sets_pane()

    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key.Key_Delete, QtCore.Qt.Key.Key_Backspace]:
            self.delete_set()
        else:
            QtWidgets.QDialog.keyPressEvent(self, event)

    def change_widget(self, index):
        self.saved_sets.clearSelection()

    def activate(self):
        ActivateCardsDialog.activate(self)
        self.exec()

    def update_saved_sets_pane(self):
        self.saved_sets.clear()
        self.criteria_by_name = {}
        active_name = ""
        active_criterion = self.database().current_criterion()
        for criterion in self.database().criteria():
            if criterion._id != 1:
                self.criteria_by_name[criterion.name] = criterion
                self.saved_sets.addItem(criterion.name)
                if criterion == active_criterion:
                    active_name = criterion.name
        self.saved_sets.sortItems()
        if active_name:
            item = self.saved_sets.findItems(active_name,
                QtCore.Qt.MatchFlag.MatchExactly)[0]
            self.saved_sets.setCurrentItem(item)
            self.was_showing_a_saved_set = True
        else:
            self.saved_sets.clearSelection()
            self.was_showing_a_saved_set = False
        splitter_sizes = self.splitter.sizes()
        if self.saved_sets.count() == 0:
            self.splitter.setSizes([0, sum(splitter_sizes)])
        else:
            if splitter_sizes[0] == 0: # First time we add a set.
                self.splitter.setSizes([int(0.3* sum(splitter_sizes)),
                    int(0.7 * sum(splitter_sizes))])

    def saved_sets_custom_menu(self, pos):
        menu = QtWidgets.QMenu()
        menu.addAction(_("Delete"), self.delete_set)
        menu.addAction(_("Rename"), self.rename_set)
        menu.exec(self.saved_sets.mapToGlobal(pos))

    def save_set(self):
        criterion = self.tab_widget.currentWidget().criterion()
        if criterion.is_empty():
            self.main_widget().show_error(\
                _("This set can never contain any cards!"))
            return
        CardSetNameDlg(criterion, self.criteria_by_name.keys(),
                       component_manager=self.component_manager, parent=self).exec()
        if not criterion.name:  # User cancelled.
            return
        if criterion.name in self.criteria_by_name.keys():
            answer = self.main_widget().show_question(_("Update this set?"),
                _("&OK"), _("&Cancel"), "")
            if answer == 1:  # Cancel.
                return
            original_criterion = self.criteria_by_name[criterion.name]
            criterion._id = original_criterion._id
            criterion.id = original_criterion.id
            self.database().update_criterion(criterion)
        else:
            self.database().add_criterion(criterion)
        self.update_saved_sets_pane()
        item = self.saved_sets.findItems(criterion.name,
            QtCore.Qt.MatchFlag.MatchExactly)[0]
        self.saved_sets.setCurrentItem(item)
        if self.config()["showed_help_on_renaming_sets"] == False:
            self.main_widget().show_information(\
                _("You can right-click on the name of a saved set to rename or delete it."))
            self.config()["showed_help_on_renaming_sets"] = True

    def delete_set(self):
        if not self.saved_sets.currentItem():
            return
        answer = self.main_widget().show_question(_("Delete this set?"),
            _("&OK"), _("&Cancel"), "")
        if answer == 1:  # Cancel.
            return -1
        else:
            name = self.saved_sets.currentItem().text()
            criterion = self.criteria_by_name[name]
            self.database().delete_criterion(criterion)
            self.database().save()
            self.update_saved_sets_pane()

    def rename_set(self):
        name = self.saved_sets.currentItem().text()
        criterion = self.criteria_by_name[name]
        criterion.name = name
        other_names = list(self.criteria_by_name.keys())
        other_names.remove(name)
        CardSetNameDlg(criterion, other_names,
                       component_manager=self.component_manager,
                       parent=self).exec()
        if criterion.name == name:  # User cancelled.
            return
        self.database().update_criterion(criterion)
        self.database().save()
        self.update_saved_sets_pane()
        item = self.saved_sets.findItems(criterion.name,
            QtCore.Qt.MatchFlag.MatchExactly)[0]
        self.saved_sets.setCurrentItem(item)

        # load_set gets triggered by ItemActivated, but this does not happen
        # when the user changes the sets through the arrow keys (Qt bug?).
        # Therefore, we also catch currentItemChanged and forward it to
        # change_set, but to prevent unwanted firing when loading the widget
        # for the first time (which would erase the current criterion in case
        # it is not a saved criterion), we discard this event if previous_item
        # is None.
        #
        # To test when editing this code: initial start, with and without
        # current criterion being a saved criterion, changing the set through
        # clicking or through the arrows.

    def load_set(self, item, dummy=None):
        # Sometimes item is None, e.g. during the process of deleting a saved
        # set, so we need to discard the event then.
        if item is None:
            return
        name = item.text()
        criterion = self.criteria_by_name[name]
        self.tab_widget.setCurrentWidget(self.widget_for_criterion_type\
                                             [criterion.criterion_type])
        self.tab_widget.currentWidget().display_criterion(criterion)
        # Restore the selection that got cleared in change_widget.
        item = self.saved_sets.findItems(criterion.name,
            QtCore.Qt.MatchFlag.MatchExactly)[0]
        self.saved_sets.setCurrentItem(item)
        self.was_showing_a_saved_set = True

    def change_set(self, item, previous_item):
        if previous_item is not None:
            self.load_set(item)

    def select_set_and_close(self, item):
        self.load_set(item)
        # Work around a Qt bug where these calls would still fire when clicking
        # in the same area where e.g. the tag browser used to be, even after
        # closing the 'Activate cards' window.
        self.is_shutting_down = True
        self.accept()

    def _store_state(self):
        self.config()["activate_cards_dlg_state"] = \
            self.saveGeometry()
        self.config()["activate_cards_dlg_splitter_state"] = \
            self.splitter.saveState()

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()
        # This allows the state of the tag tree to be saved.
        self.tab_widget.currentWidget().close()

    def accept(self):
        criterion = self.tab_widget.currentWidget().criterion()
        if criterion.is_empty():
            self.main_widget().show_error(\
                _("This set can never contain any cards!"))
            return
        if self.saved_sets.count() != 0 and self.config()\
            ["showed_help_on_double_clicking_sets"] == False:
            self.main_widget().show_information(\
_("You can double-click on the name of a saved set to activate it and close the dialog."))
            self.config()["showed_help_on_double_clicking_sets"] = True
        if len(self.saved_sets.selectedItems()) > 0:
            criterion.name = self.saved_sets.currentItem().text()
        self.database().set_current_criterion(criterion)
        # 'accept' does not generate a close event.
        self._store_state()
        return QtWidgets.QDialog.accept(self)
