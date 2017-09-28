#
# manage_card_types_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.pyqt_ui.clone_card_type_dlg import CloneCardTypeDlg
from mnemosyne.pyqt_ui.ui_manage_card_types_dlg import Ui_ManageCardTypesDlg
from mnemosyne.pyqt_ui.edit_M_sided_card_type_dlg import EditMSidedCardTypeDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ManageCardTypesDialog


class ManageCardTypesDlg(QtWidgets.QDialog, ManageCardTypesDialog,
                         Ui_ManageCardTypesDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.update()
        state = self.config()["manage_card_types_dlg_state"]
        if state:
            self.restoreGeometry(state)

    def activate(self):
        ManageCardTypesDialog.activate(self)
        self.exec_()

    def update(self):
        self.cloned_card_types.clear()
        self.M_sided_card_types.clear()
        self.items_used = []
        self.card_types_used = []
        # Fill up cloned card types panel.
        for card_type in self.database().sorted_card_types():
            if self.database().is_user_card_type(card_type) and \
               not card_type.hidden_from_UI and \
               not card_type.id.startswith("7"):
                name = "%s (%s)" % (_(card_type.name),
                                    _(card_type.__class__.__bases__[0].name))
                item = QtWidgets.QListWidgetItem(name)
                self.cloned_card_types.addItem(item)
                # Since node_item seems mutable, we cannot use a dict.
                self.items_used.append(item)
                self.card_types_used.append(card_type)
        self.rename_clone_button.setEnabled(False)
        self.delete_clone_button.setEnabled(False)
        # Fill up M-sided card types panel.
        for card_type in self.database().sorted_card_types():
            if self.database().is_user_card_type(card_type) and \
               not card_type.hidden_from_UI and \
               card_type.id.startswith("7"):
                item = QtWidgets.QListWidgetItem(card_type.name)
                self.M_sided_card_types.addItem(item)
                # Since node_item seems mutable, we cannot use a dict.
                self.items_used.append(item)
                self.card_types_used.append(card_type)
        self.edit_M_sided_button.setEnabled(False)
        self.rename_M_sided_button.setEnabled(False)
        self.delete_M_sided_button.setEnabled(False)
        if self.M_sided_card_types.count() == 0:
            self.M_sided_card_types_box.hide()

    def clone_card_type(self):
        if not self.config()["clone_help_shown"]:
            self.main_widget().show_information(\
_("Here, you can make clones of existing card types. This allows you to format cards in this type independently from cards in the original type. E.g. you can make a clone of 'Vocabulary', call it 'Thai' and set a Thai font specifically for this card type without disturbing your other cards."))
            self.config()["clone_help_shown"] = True
        dlg = CloneCardTypeDlg(parent=self, component_manager=self.component_manager)
        dlg.exec_()
        self.update()

    def activate_cloned_card_type(self):
        self.rename_clone_button.setEnabled(True)
        self.delete_clone_button.setEnabled(True)
        self.edit_M_sided_button.setEnabled(False)
        self.rename_M_sided_button.setEnabled(False)
        self.delete_M_sided_button.setEnabled(False)

    def activate_M_sided_card_type(self):
        self.rename_clone_button.setEnabled(False)
        self.delete_clone_button.setEnabled(False)
        self.edit_M_sided_button.setEnabled(True)
        self.rename_M_sided_button.setEnabled(True)
        self.delete_M_sided_button.setEnabled(True)

    def delete_cloned_card_type(self):
        self.delete_selected_card_type(self.cloned_card_types.selectedItems())

    def delete_M_sided_card_type(self):
        self.delete_selected_card_type(self.M_sided_card_types.selectedItems())

    def delete_selected_card_type(self, selected_items):
        if len(selected_items) == 0:
            return
        answer = self.main_widget().show_question\
            (_("Delete this card type?"), _("&OK"), _("&Cancel"), "")
        if answer == 1: # Cancel.
            return
        selected_item = selected_items[0]
        for i in range(len(self.items_used)):
            if selected_item == self.items_used[i]:
                card_type = self.card_types_used[i]
                self.controller().delete_card_type(card_type)
                self.update()
                return

    def rename_cloned_card_type(self):
        self.rename_selected_card_type(self.cloned_card_types.selectedItems())

    def rename_M_sided_card_type(self):
        self.rename_selected_card_type(self.M_sided_card_types.selectedItems())

    def rename_selected_card_type(self, selected_items):
        if len(selected_items) == 0:
            return

        from mnemosyne.pyqt_ui.ui_rename_card_type_dlg \
            import Ui_RenameCardTypeDlg

        class RenameDlg(QtWidgets.QDialog, Ui_RenameCardTypeDlg):
            def __init__(self, old_card_type_name):
                super().__init__()
                self.setupUi(self)
                self.card_type_name.setText(old_card_type_name)

        selected_item = selected_items[0]
        for i in range(len(self.items_used)):
            if selected_item == self.items_used[i]:
                card_type = self.card_types_used[i]
                dlg = RenameDlg(card_type.name)
                if dlg.exec_() == QtWidgets.QDialog.Accepted:
                    new_name = dlg.card_type_name.text()
                    self.controller().rename_card_type(card_type, new_name)
                self.update()
                return

    def edit_M_sided_card_type(self):
        selected_items = self.M_sided_card_types.selectedItems()
        if len(selected_items) == 0:
            return
        selected_item = selected_items[0]
        for i in range(len(self.items_used)):
            if selected_item == self.items_used[i]:
                card_type = self.card_types_used[i]
                dlg = EditMSidedCardTypeDlg(card_type,
                    component_manager=self.component_manager)
                if dlg.exec_() == QtWidgets.QDialog.Accepted:
                    self.database().update_card_type(card_type)
                self.update()
                return

    def _store_state(self):
        self.config()["manage_card_types_dlg_state"] = self.saveGeometry()

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()

    def accept(self):
        self._store_state()
        return QtWidgets.QDialog.accept(self)

    def reject(self):
        self._store_state()
        return QtWidgets.QDialog.reject(self)

