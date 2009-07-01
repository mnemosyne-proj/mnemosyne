#
# edit_fact_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_edit_fact_dlg import Ui_EditFactDlg

from mnemosyne.pyqt_ui.generic_card_type_widget import GenericCardTypeWdgt
from mnemosyne.pyqt_ui.add_cards_dlg import AddEditCards
from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
from mnemosyne.pyqt_ui.convert_card_type_fields_dlg import \
                                                    ConvertCardTypeFieldsDlg


class EditFactDlg(QDialog, Ui_EditFactDlg, AddEditCards):

    def __init__(self, fact, parent, component_manager, allow_cancel=True):
        AddEditCards.__init__(self, component_manager)
        QDialog.__init__(self, parent)
        self.setupUi(self)
        if not allow_cancel:
            self.exit_button.setVisible(False)  
        self.fact = fact 
        self.initialise_card_types_combobox(self.fact.card_type.name)     
        tag_string = ""
        for tag in self.database().cards_from_fact(fact)[0].tags:
            tag_string += tag.name + ", "
        tag_string = tag_string[:-2]
        self.update_tags_combobox(tag_string)

    def set_valid(self, valid):
        self.OK_button.setEnabled(valid)    
        self.preview_button.setEnabled(valid)
        
    def accept(self):
        new_fact_data = self.card_type_widget.get_data()
        new_tag_names = [tag.strip() for tag in \
                        unicode(self.tags.currentText()).split(',')]
        new_card_type_name = unicode(self.card_types_widget.currentText())
        new_card_type = self.card_type_by_name[new_card_type_name]
        c = self.ui_controller_main()
        status = c.update_related_cards(self.fact, new_fact_data,
                        new_card_type, new_tag_names, self.correspondence)
        if status == 0:
            tag_text = ", ".join(new_tag_names)
            self.config()["tags_of_last_added"] = tag_text
            QDialog.accept(self)

    def reject(self): # Override 'add cards' behaviour.
        QDialog.reject(self)
        
