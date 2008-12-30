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
from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
from mnemosyne.pyqt_ui.convert_card_type_fields_dlg import \
                                                    ConvertCardTypeFieldsDlg


class EditFactDlg(QDialog, Ui_EditFactDlg):

    def __init__(self, fact, parent=None):
        QDialog.__init__(self, parent)
        # TODO: modal, Qt.WStyle_MinMax | Qt.WStyle_SysMenu))?
        self.setupUi(self)
        self.fact = fact
        # We calculate card_type_by_name here rather than in the component
        # manager, because these names can change if the user chooses another
        # translation. TODO: test.
        self.card_type_by_name = {}
        for card_type in card_types():
            self.card_types.addItem(card_type.name)
            self.card_type_by_name[card_type.name] = card_type
        # TODO: sort card types by id.
        # TODO: remember last type.
        
        self.card_widget = None
        self.update_card_widget()
        cat_string = ""
        for cat in self.fact.cat:
            cat_string += cat.name + ", "
        cat_string = cat_string[:-2]
        self.update_combobox(cat_string)

        #TODO: fonts?
        #if config()("QA_font") != None:
        #    font = QFont()
        #    font.fromString(config()("QA_font"))
        #    self.question.setFont(font)
        #    self.pronunciation.setFont(font)
        #    self.answer.setFont(font)
        #self.categories.setFont(font)

    def update_card_widget(self):
        if self.card_widget:
            prefill_data = self.card_widget.get_data(check_for_required=False)
            self.verticalLayout.removeWidget(self.card_widget)
            self.card_widget.close()
            del self.card_widget
        else:
            prefill_data = self.fact.data
        card_type_name = unicode(self.card_types.currentText())
        card_type = self.card_type_by_name[card_type_name]
        try:
            card_type.widget = component_manager.get_current\
                       ("card_type_widget",
                       used_for=card_type.__class__.__name__)\
                           (parent=self, prefill_data=prefill_data)
        except:
            card_type.widget = GenericCardTypeWdgt\
                           (card_type, parent=self, prefill_data=prefill_data)
        self.card_widget = card_type.widget
        self.card_widget.show()
        self.verticalLayout.insertWidget(1, self.card_widget)
        #self.adjustSize()

    def update_combobox(self, current_cat_name):
        no_of_categories = self.categories.count()
        for i in range(no_of_categories-1,-1,-1):
            self.categories.removeItem(i)
        self.categories.addItem(_("<default>"))
        for name in database().category_names():
            if name != _("<default>"):
                self.categories.addItem(name)
        if ',' in current_cat_name:
            self.categories.addItem(current_cat_name)      
        for i in range(self.categories.count()):
            if self.categories.itemText(i) == current_cat_name:
                self.categories.setCurrentIndex(i)
                break
            
    def accept(self):
        try:
            new_fact_data = self.card_widget.get_data()
        except ValueError:
            return # Let the user try again to fill out the missing data.
        new_cat_names = [c.strip() for c in \
                        unicode(self.categories.currentText()).split(',')]
        new_card_type_name = unicode(self.card_types.currentText())
        new_card_type = self.card_type_by_name[new_card_type_name]
        if new_card_type != self.fact.card_type:
            if not self.fact.card_type.keys().issubset(new_card_type.keys()):
                dlg = ConvertCardTypeFieldsDlg(self.fact.card_type,
                                               new_card_type, self)
                field_map = dlg.exec_()
                print field_map
            else:
                print 'no conversion needed'

        # TODO: run card type convertors
        c = ui_controller_main()
        c.update_related_cards(self.fact, new_fact_data, new_card_type, \
                               new_cat_names)
        QDialog.accept(self)

    def preview(self):
        fact_data = self.card_widget.get_data(check_for_required=False)
        card_type_name = unicode(self.card_types.currentText())
        card_type = self.card_type_by_name[card_type_name]
        cards = card_type.create_related_cards(Fact(fact_data, card_type))
        cat_text = self.categories.currentText()
        if cat_text == _("<default>"):
            cat_text = ""
        dlg = PreviewCardsDlg(cards, cat_text, self)
        dlg.exec_()
