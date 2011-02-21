#
# activate_cards_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.card_set_name_dlg import CardSetNameDlg
from mnemosyne.pyqt_ui.ui_activate_cards_dlg import Ui_ActivateCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog


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
        # Initialise widgets.
        QtGui.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Delete),
                        self.saved_sets, self.delete_set)
        criterion = self.database().current_criterion()
        self.criterion_classes = \
            self.component_manager.all("criterion")       
        current_criterion = self.database().current_criterion()
        self.widget_for_criterion_type = {}
        for criterion_class in self.criterion_classes:
            widget = self.component_manager.current\
                ("criterion_widget", used_for=criterion_class)\
                (self.component_manager, self)
            self.tab_widget.addTab(widget, criterion_class.criterion_type)
            self.widget_for_criterion_type[criterion_class.criterion_type] \
                = widget
        self.tab_widget.setCurrentWidget(self.widget_for_criterion_type\
                                         [current_criterion.criterion_type])
        self.tab_widget.tabBar().setVisible(self.tab_widget.count() > 1)
        self.tab_widget.currentWidget().display_criterion(current_criterion)           
        # Should go last, otherwise the selection of the saved sets pane will
        # always be cleared.
        self.update_saved_sets_pane()

    def change_widget(self, index):
        self.saved_sets.clearSelection()

    def activate(self):
        self.exec_()

    def update_saved_sets_pane(self):
        self.saved_sets.clear()
        self.criteria_by_name = {}
        active_name = ""
        active_criterion = self.database().current_criterion()
        for criterion in self.database().criteria():
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

    def saved_sets_custom_menu(self, pos):
        menu = QtGui.QMenu()
        menu.addAction(_("Delete"), self.delete_set)
        menu.addAction(_("Rename"), self.rename_set)
        menu.exec_(self.saved_sets.mapToGlobal(pos))
        
    def save_set(self):
        criterion = self.tab_widget.currentWidget().criterion()
        CardSetNameDlg(self.component_manager, criterion,
                       self.criteria_by_name.keys()).exec_()
        if not criterion.name:  # User cancelled.
            return
        self.database().add_criterion(criterion)
        self.update_saved_sets_pane()
        item = self.saved_sets.findItems(criterion.name,
            QtCore.Qt.MatchExactly)[0]
        self.saved_sets.setCurrentItem(item)
        
    def delete_set(self):
        answer = self.main_widget().show_question(_("Delete this set?"),
            _("&OK"), _("&Cancel"), "")
        if answer == 1:  # Cancel.
            return -1
        else:
            name = unicode(self.saved_sets.currentItem().text())
            criterion = self.criteria_by_name[name]
            self.database().delete_criterion(criterion)
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
        self.database().update_criterion(criterion)
        self.database().save()
        self.update_saved_sets_pane()
        item = self.saved_sets.findItems(criterion.name,
            QtCore.Qt.MatchExactly)[0]
        self.saved_sets.setCurrentItem(item)

    def load_set(self, item):
        name = unicode(item.text())
        criterion = self.criteria_by_name[name]
        self.tab_widget.setCurrentWidget(self.widget_for_criterion_type\
                                             [criterion.criterion_type])
        self.tab_widget.currentWidget().display_criterion(criterion)
        # Restore the selection that got cleared in change_widget.
        item = self.saved_sets.findItems(criterion.name,
            QtCore.Qt.MatchExactly)[0]
        self.saved_sets.setCurrentItem(item)
            
    def _store_layout(self):
        self.config()["activate_cards_dlg_size"] = \
            (self.width(), self.height())
        self.config()["activate_cards_dlg_splitter"] = \
            self.splitter.sizes()
        
    def closeEvent(self, event):
        self._store_layout()
        
    def accept(self):
        self.database().set_current_criterion(\
            self.tab_widget.currentWidget().criterion())
        self._store_layout()
        return QtGui.QDialog.accept(self)
        
    def reject(self):
        self._store_layout()
        QtGui.QDialog.reject(self)
