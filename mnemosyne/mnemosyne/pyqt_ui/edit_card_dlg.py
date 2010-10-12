#
# edit_card_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.pyqt_ui.add_cards_dlg import AddEditCards
from mnemosyne.pyqt_ui.ui_edit_card_dlg import Ui_EditCardDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import EditCardDialog


class EditCardDlg(QtGui.QDialog, Ui_EditCardDlg, AddEditCards,
                  EditCardDialog):

    def __init__(self, card, component_manager, allow_cancel=True):
        AddEditCards.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        if not allow_cancel:
            self.exit_button.setVisible(False)  
        self.card = card
        self.initialise_card_types_combobox(self.card.card_type.name)     
        self.update_tags_combobox(card.tag_string())
        width, height = self.config()["edit_widget_size"]
        if width:
            self.resize(width, height)
            
    def closeEvent(self, event):
        self.config()["edit_widget_size"] = (self.width(), self.height())
    
    def set_valid(self, valid):
        self.OK_button.setEnabled(valid)    
        self.preview_button.setEnabled(valid)
        
    def accept(self):
        self.config()["edit_widget_size"] = (self.width(), self.height())
        new_fact_data = self.card_type_widget.data()
        new_tag_names = [tag.strip() for tag in \
            unicode(self.tags.currentText()).split(',')]
        new_card_type_name = unicode(self.card_types_widget.currentText())
        new_card_type = self.card_type_by_name[new_card_type_name]
        c = self.controller()
        status = c.edit_related_cards(self.card.fact, new_fact_data,
            new_card_type, new_tag_names, self.correspondence)
        if status == 0:
            tag_text = ", ".join(new_tag_names)
            self.config()["tags_of_last_added"] = tag_text
            QtGui.QDialog.accept(self)

    def reject(self): # Override 'add cards' behaviour.
        self.config()["edit_widget_size"] = (self.width(), self.height())
        QtGui.QDialog.reject(self)
        
