#
# edit_fact_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_edit_fact_dlg import Ui_EditFactDlg

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import config, ui_controller_main
from mnemosyne.libmnemosyne.component_manager import database, card_types
from mnemosyne.pyqt_ui.generic_card_type_widget import GenericCardTypeWdgt
from mnemosyne.pyqt_ui.add_cards_dlg import AddEditCards
from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
from mnemosyne.pyqt_ui.convert_card_type_fields_dlg import \
                                                    ConvertCardTypeFieldsDlg


class EditFactDlg(QDialog, Ui_EditFactDlg, AddEditCards):

    def __init__(self, fact, allow_cancel=True, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        if not allow_cancel:
            self.exit_button.setVisible(False)  
        self.fact = fact 
        self.initialise_card_types_combobox(self.fact.card_type)     
        cat_string = ""
        for cat in self.fact.cat:
            cat_string += cat.name + ", "
        cat_string = cat_string[:-2]
        self.update_categories_combobox(cat_string)

    def is_complete(self, complete):
        self.OK_button.setEnabled(complete)    
            
    def accept(self):
        new_fact_data = self.card_type.widget.get_data()
        new_cat_names = [c.strip() for c in \
                        unicode(self.categories.currentText()).split(',')]
        new_card_type_name = unicode(self.card_types.currentText())
        new_card_type = self.card_type_by_name[new_card_type_name]
        c = ui_controller_main()
        status = c.update_related_cards(self.fact, new_fact_data,
                        new_card_type, new_cat_names, self.correspondence)
        if status == 0:
            QDialog.accept(self)

    def reject(self): # Override 'add cards' behaviour.
        QDialog.reject(self)
        
