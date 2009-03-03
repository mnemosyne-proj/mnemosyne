#
# add_cards_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_add_cards_dlg import Ui_AddCardsDlg

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.utils import numeric_string_cmp
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import config, ui_controller_main
from mnemosyne.libmnemosyne.component_manager import database, card_types
from mnemosyne.pyqt_ui.generic_card_type_widget import GenericCardTypeWdgt
from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
from mnemosyne.pyqt_ui.convert_card_type_fields_dlg import \
                                                    ConvertCardTypeFieldsDlg

class AddEditCards:

    """Code shared between the add and the edit dialogs."""

    def initialise_card_types_combobox(self, current_card_type_name):
        # We calculate card_type_by_name here rather than in the component
        # manager, because these names can change if the user chooses another
        # translation.
        self.card_type_by_name = {}
        self.card_type = None
        self.card_type_index = 0   
        for card_type in card_types():
            if card_type.name == current_card_type_name:
                self.card_type = card_type
                self.card_type_index = self.card_types.count()
            self.card_type_by_name[card_type.name] = card_type
            self.card_types.addItem(card_type.name)
        if not self.card_type:
            self.card_type = card_types()[0]
            self.card_type_index = 0
        self.card_types.setCurrentIndex(self.card_type_index)
        self.connect(self.card_types, SIGNAL("currentIndexChanged(QString)"),
                     self.card_type_changed)
        self.correspondence = {} # Used when changing card types.
        self.update_card_widget()
        
    def update_card_widget(self):
        # Determine data to put into card widget. Since we want to share this
        # code between the 'add' and the 'edit' dialogs, we put the reference
        # to self.fact (which only exists in the 'edit' dialog) insid a try
        # statement.
        if self.card_type.widget: # Get data from previous card widget.
            prefill_data = \
                     self.card_type.widget.get_data(check_for_required=False)
            self.card_type.widget.close()
            self.card_type.widget = None
        else:
            try: # Get data from fact passed to the 'edit' dialog.
                prefill_data = self.fact.data
            except: # Start from scratch in the 'add' dialog.
                prefill_data = None
                
        # Transform keys in dictionary if the card type has changed, but don't
        # update the fact just yet.
        if prefill_data:
            for key in prefill_data:
                if key in self.correspondence:
                    value = prefill_data.pop(key)
                    prefill_data[self.correspondence[key]] = value
    
        # Show new card type widget.
        card_type_name = unicode(self.card_types.currentText())
        self.card_type = self.card_type_by_name[card_type_name]
        try:                                                                    
            self.card_type.widget = component_manager.get_current\
                       ("card_type_widget", used_for=card_type.__class__)\
                          (parent=self, prefill_data=prefill_data)
        except:
            if not self.card_type.widget: 
                self.card_type.widget = GenericCardTypeWdgt\
                      (self.card_type, parent=self, prefill_data=prefill_data)
        self.card_type.widget.show()
        self.verticalLayout.insertWidget(1, self.card_type.widget)

    def update_categories_combobox(self, current_cat_name):
        self.categories.clear()
        self.categories.addItem(_("<default>"))
        sorted_categories = sorted(database().category_names(), cmp=numeric_string_cmp)
        for name in sorted_categories:
            if name != _("<default>"):
                self.categories.addItem(name)
        if ',' in current_cat_name:
            self.categories.addItem(current_cat_name)      
        for i in range(self.categories.count()):
            if self.categories.itemText(i) == current_cat_name:
                self.categories.setCurrentIndex(i)
                break

    def card_type_changed(self, new_card_type_name):
        new_card_type_name = unicode(new_card_type_name)
        config()["card_type_name_of_last_added"] = new_card_type_name
        new_card_type = self.card_type_by_name[new_card_type_name]
        if self.card_type.keys().issubset(new_card_type.keys()) or \
               not self.card_type.widget.contains_data():
            self.update_card_widget()            
            return
        dlg = ConvertCardTypeFieldsDlg(self.card_type, new_card_type,
                                       self.correspondence, self)
        if dlg.exec_() == 0: # Reject.
            self.card_types.setCurrentIndex(self.card_type_index)
            return
        else:          
            self.update_card_widget()

    def preview(self):
        fact_data = self.card_type.widget.get_data(check_for_required=False)
        fact = Fact(fact_data, self.card_type)
        cards = self.card_type.create_related_cards(fact)
        cat_text = self.categories.currentText()
        if cat_text == _("<default>"):
            cat_text = ""
        dlg = PreviewCardsDlg(cards, cat_text, self)
        dlg.exec_()

    def __del__(self):
        # Make sure that Python knows Qt has deleted this widget.
        self.card_type.widget = None        


class AddCardsDlg(QDialog, Ui_AddCardsDlg, AddEditCards):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.initialise_card_types_combobox(\
            config()["card_type_name_of_last_added"])
        self.update_categories_combobox(\
            config()["categories_of_last_added"])  
        self.grades = QButtonGroup()
        self.grades.addButton(self.grade_0_button, 0)
        self.grades.addButton(self.grade_1_button, 1)
        self.grades.addButton(self.grade_2_button, 2)
        self.grades.addButton(self.grade_3_button, 3)
        self.grades.addButton(self.grade_4_button, 4)
        self.grades.addButton(self.grade_5_button, 5)
        self.connect(self.grades, SIGNAL("buttonClicked(int)"),
                     self.new_cards)
        self.is_complete(False)
         
    def is_complete(self, complete):
        self.grade_buttons.setEnabled(complete)
        
    def new_cards(self, grade):
        fact_data = self.card_type.widget.get_data()
        cat_names = [c.strip() for c in \
                     unicode(self.categories.currentText()).split(',')]
        card_type_name = unicode(self.card_types.currentText())
        card_type = self.card_type_by_name[card_type_name]
        c = ui_controller_main()
        c.create_new_cards(fact_data, card_type, grade, cat_names)
        cat_text = ', '.join(cat_names)
        self.update_categories_combobox(cat_text)
        config()["categories_of_last_added"] = cat_text
        database().save(config()['path'])
        self.card_type.widget.clear()

    def reject(self):
        if self.card_type.widget.contains_data():
            status = QMessageBox.warning(None, _("Mnemosyne"),
                                         _("Abandon current card?"),
                                         _("&Yes"), _("&No"), "", 1, -1)
            if status == 0:
                QDialog.reject(self)
                return
        else:
            QDialog.reject(self)


