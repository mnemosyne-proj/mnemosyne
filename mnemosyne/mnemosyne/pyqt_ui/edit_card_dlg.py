#
# edit_card_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.add_cards_dlg import AddEditCards
from mnemosyne.pyqt_ui.ui_edit_card_dlg import Ui_EditCardDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import EditCardDialog


class EditCardDlg(QtGui.QDialog, Ui_EditCardDlg, AddEditCards,
                  EditCardDialog):

    def __init__(self, card, component_manager, allow_cancel=True):
        # Note: even though this is in essence an EditFactDlg, we don't use
        # 'fact' as argument, as 'fact' does not know anything about card
        # types.
        AddEditCards.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint) 
        self.before_apply_hook = None
        self.allow_cancel = allow_cancel
        if not allow_cancel:
            self.exit_button.setVisible(False)  
        self.card = card
        self.initialise_card_types_combobox(self.card.card_type.name)
        self.update_tags_combobox(card.tag_string())
        state = self.config()["edit_card_dlg_state"]
        if state:
            self.restoreGeometry(state)

    def activate(self):
        self.retranslateUi(self)

    def _store_state(self):
        self.config()["edit_card_dlg_state"] = self.saveGeometry()
            
    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()
        if self.allow_cancel:
            event.accept()
            QtGui.QDialog.reject(self)
        else:
            self.main_widget().show_information(\
                _("You are not allowed to cancel the merging."))
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            if self.allow_cancel:
                self.reject()
            else:
                self.main_widget().show_information(\
                    _("You are not allowed to cancel the merging."))
                event.ignore()                
 
    def set_valid(self, valid):
        self.OK_button.setEnabled(valid)    
        self.preview_button.setEnabled(valid)
        
    def accept(self):
        self._store_state()
        new_fact_data = self.card_type_widget.fact_data()
        new_tag_names = [tag.strip() for tag in \
            unicode(self.tags.currentText()).split(',')]
        new_card_type_name = unicode(self.card_types_widget.currentText())
        new_card_type = self.card_type_by_name[new_card_type_name]
        if self.before_apply_hook:
            self.before_apply_hook()
        status = self.controller().edit_sister_cards(self.card.fact,
            new_fact_data, self.card.card_type, new_card_type, new_tag_names,
            self.correspondence)
        if status == 0:
            tag_text = ", ".join(new_tag_names)
            self.config()["last_used_tags_for_card_type_id"][new_card_type.id] \
                = tag_text
            self.config()["edit_widget_size"] = (self.width(), self.height())
            QtGui.QDialog.accept(self)

    def reject(self):  # Override 'add cards' behaviour.
        QtGui.QDialog.reject(self)
