#
# manage_card_types_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.pyqt_ui.clone_card_type_dlg import CloneCardTypeDlg
from mnemosyne.pyqt_ui.ui_manage_card_types_dlg import Ui_ManageCardTypesDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ManageCardTypesDialog


class ManageCardTypesDlg(QtGui.QDialog, Ui_ManageCardTypesDlg,
                        ManageCardTypesDialog):

    def __init__(self, component_manager):
        ManageCardTypesDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.update()

    def activate(self):
        self.exec_()

    def update(self):
        self.cloned_card_types.clear()
        self.card_type_with_item = {}
        for card_type in self.card_types():
            if self.database().is_user_card_type(card_type):
                name = "%s (%s)" % (_(card_type.name),
                                    _(card_type.__class__.__bases__[0].name))
                item = QtGui.QListWidgetItem(name)
                self.cloned_card_types.addItem(item)
                self.card_type_with_item[item] = card_type
        if self.cloned_card_types.count() == 0:
            self.rename_button.setEnabled(False)
            self.delete_button.setEnabled(False)
        else:
            self.rename_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.cloned_card_types.item(0).setSelected(True)

    def clone_card_type(self):
        if not self.config()["clone_help_shown"]:
            self.main_widget().show_information(\
_("Here, you can make clones of existing card types. This allows you to format cards in this type independently from cards in the original type. E.g. you can make a clone of 'Vocabulary', call it 'Thai' and set a Thai font specifically for this card type without disturbing your other cards."))
            self.config()["clone_help_shown"] = True
        dlg = CloneCardTypeDlg(self, self.component_manager)
        dlg.exec_()
        self.update()

    def delete_card_type(self):
        if len(self.cloned_card_types.selectedItems()) == 0:
            return
        answer = self.main_widget().show_question\
            (_("Delete this card type?"), _("&OK"), _("&Cancel"), "")
        if answer == 1: # Cancel.
            return
        card_type = self.card_type_with_item\
            [self.cloned_card_types.selectedItems()[0]]
        self.controller().delete_card_type(card_type)
        self.update()

    def rename_card_type(self):
        if len(self.cloned_card_types.selectedItems()) == 0:
            return

        from mnemosyne.pyqt_ui.ui_rename_card_type_dlg \
            import Ui_RenameCardTypeDlg

        class RenameDlg(QtGui.QDialog, Ui_RenameCardTypeDlg):
            def __init__(self, old_card_type_name):
                QtGui.QDialog.__init__(self)
                self.setupUi(self)
                self.card_type_name.setText(old_card_type_name)

        card_type = self.card_type_with_item\
            [self.cloned_card_types.selectedItems()[0]]
        dlg = RenameDlg(card_type.name)
        if dlg.exec_() == QtGui.QDialog.Accepted:
            new_name = unicode(dlg.card_type_name.text())
            self.controller().rename_card_type(card_type, new_name)
        self.update()
