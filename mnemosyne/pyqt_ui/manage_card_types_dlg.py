#
# manage_card_types_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.pyqt_ui.card_type_language_list_wdgt import \
     CardTypeLanguageListWdgt
from mnemosyne.pyqt_ui.clone_card_type_dlg import CloneCardTypeDlg
from mnemosyne.pyqt_ui.ui_manage_card_types_dlg import Ui_ManageCardTypesDlg
from mnemosyne.pyqt_ui.edit_M_sided_card_type_dlg import EditMSidedCardTypeDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ManageCardTypesDialog


class ManageCardTypesDlg(QtWidgets.QDialog, ManageCardTypesDialog,
                         Ui_ManageCardTypesDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.native_card_types = CardTypeLanguageListWdgt(\
            parent=self.native_card_types_box,
            component_manager=self.component_manager)
        self.vertical_layout_native_card_types.insertWidget(\
            0, self.native_card_types)
        self.Anki_card_types = CardTypeLanguageListWdgt(\
            parent=self.Anki_card_types_box,
            component_manager=self.component_manager)
        self.vertical_layout_Anki_card_types.insertWidget(\
            0, self.Anki_card_types)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.update()
        state = self.config()["manage_card_types_dlg_state"]
        if state:
            self.restoreGeometry(state)

    def activate(self):
        ManageCardTypesDialog.activate(self)
        self.exec()

    def update(self):
        # Fill up native types panel.
        card_types = []
        for card_type in self.database().sorted_card_types():
            if not card_type.hidden_from_UI and \
               not card_type.id.startswith("7"):
                card_types.append(card_type)
        self.native_card_types.set_card_types(card_types)
        self.rename_native_card_type_button.setEnabled(False)
        self.delete_native_card_type_button.setEnabled(False)
        self.native_card_types.selectionModel().currentRowChanged.connect(\
            self.activate_native_card_type)
        # Fill up Anki card types panel.
        card_types = []
        for card_type in self.database().sorted_card_types():
            if self.database().is_user_card_type(card_type) and \
               not card_type.hidden_from_UI and \
               card_type.id.startswith("7"):
                card_types.append(card_type)
        self.Anki_card_types.set_card_types(card_types)
        self.edit_Anki_card_type_button.setEnabled(False)
        self.rename_Anki_card_type_button.setEnabled(False)
        self.delete_Anki_card_type_button.setEnabled(False)
        self.Anki_card_types.selectionModel().currentRowChanged.connect(\
            self.activate_Anki_card_type)
        if len(card_types) == 0:
            self.Anki_card_types_box.hide()
        else:
            self.native_card_types_box.setTitle(_("Mnemosyne card types"))

    def clone_card_type(self):
        if not self.config()["clone_help_shown"]:
            self.main_widget().show_information(\
_("Here, you can make clones of existing card types. This allows you to format cards in this type independently from cards in the original type. E.g. you can make a clone of 'Vocabulary', call it 'Thai' and set a Thai font specifically for this card type without disturbing your other cards."))
            self.config()["clone_help_shown"] = True
        dlg = CloneCardTypeDlg(parent=self, component_manager=self.component_manager)
        dlg.exec()
        self.update()

    def activate_native_card_type(self):
        self.rename_native_card_type_button.setEnabled(True)
        self.delete_native_card_type_button.setEnabled(True)
        self.edit_Anki_card_type_button.setEnabled(False)
        self.rename_Anki_card_type_button.setEnabled(False)
        self.delete_Anki_card_type_button.setEnabled(False)

    def activate_Anki_card_type(self):
        self.rename_native_card_type_button.setEnabled(False)
        self.delete_native_card_type_button.setEnabled(False)
        self.edit_Anki_card_type_button.setEnabled(True)
        self.rename_Anki_card_type_button.setEnabled(True)
        self.delete_Anki_card_type_button.setEnabled(True)

    def delete_native_card_type(self):
        self.delete_selected_card_type(\
            self.native_card_types.selected_card_type())

    def delete_Anki_card_type(self):
        self.delete_selected_card_type(\
            self.Anki_card_types.selected_card_type())

    def delete_selected_card_type(self, card_type):
        if not card_type:
            return
        answer = self.main_widget().show_question\
            (_("Delete this card type?"), _("&OK"), _("&Cancel"), "")
        if answer == 1: # Cancel.
            return
        self.controller().delete_card_type(card_type)
        self.update()

    def rename_native_card_type(self):
        self.rename_selected_card_type(\
            self.native_card_types.selected_card_type())

    def rename_Anki_card_type(self):
        self.rename_selected_card_type(\
            self.Anki_card_types.selected_card_type())

    def rename_selected_card_type(self, card_type):
        if not card_type:
            return

        from mnemosyne.pyqt_ui.ui_rename_card_type_dlg \
            import Ui_RenameCardTypeDlg

        class RenameDlg(QtWidgets.QDialog, Ui_RenameCardTypeDlg):
            def __init__(self, old_card_type_name):
                super().__init__()
                self.setupUi(self)
                self.card_type_name.setText(old_card_type_name)

        dlg = RenameDlg(card_type.name)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            new_name = dlg.card_type_name.text()
            self.controller().rename_card_type(card_type, new_name)
            self.update()

    def edit_Anki_card_type(self):
        card_type = self.Anki_card_types.selected_card_type()
        if not card_type:
            return
        dlg = EditMSidedCardTypeDlg(card_type,
            component_manager=self.component_manager)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.database().update_card_type(card_type)
            self.update()

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

