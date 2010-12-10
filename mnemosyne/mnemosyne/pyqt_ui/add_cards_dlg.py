#
# add_cards_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import numeric_string_cmp
from mnemosyne.pyqt_ui.ui_add_cards_dlg import Ui_AddCardsDlg
from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import AddCardsDialog
from mnemosyne.pyqt_ui.card_type_wdgt_generic import GenericCardTypeWdgt
from mnemosyne.pyqt_ui.convert_card_type_fields_dlg import \
                                                    ConvertCardTypeFieldsDlg

class AddEditCards(Component):

    """Code shared between the add and the edit dialogs."""

    def activate(self):
        self.exec_()

    def initialise_card_types_combobox(self, current_card_type_name):
        # We calculate card_type_by_name here because these names can change
        # if the user chooses another translation.
        self.card_type_by_name = {}
        self.card_type = None
        self.card_type_index = 0
        self.card_type_widget = None
        for card_type in self.card_types():
            if card_type.name == current_card_type_name:
                self.card_type = card_type
                self.card_type_index = self.card_types_widget.count()
            self.card_type_by_name[card_type.name] = card_type
            self.card_types_widget.addItem(card_type.name)
        if not self.card_type:
            self.card_type = self.card_types()[0]
            self.card_type_index = 0
        self.card_types_widget.setCurrentIndex(self.card_type_index)
        # Now that the combobox is filled, we can connect the signal.
        self.card_types_widget.currentIndexChanged[QtCore.QString].\
            connect(self.card_type_changed)
        self.correspondence = {}  # Used when changing card types.
        self.update_card_widget()
        
    def update_card_widget(self):
        # Determine data to put into card widget. Since we want to share this
        # code between the 'add' and the 'edit' dialogs, we put the reference
        # to self.card (which only exists in the 'edit' dialog) inside a try
        # statement.
        if self.card_type_widget:  # Get data from previous card widget.
            prefill_data = \
                     self.card_type_widget.data()
            self.card_type_widget.close()
            self.card_type_widget = None
        else:
            try:  # Get data from fact passed to the 'edit' dialog.
                prefill_data = self.card.fact.data
            except:  # Start from scratch in the 'add' dialog.
                prefill_data = None          
        # Transform keys in dictionary if the card type has changed, but don't
        # edit the fact just yet.
        if prefill_data:
            for key in prefill_data:
                if key in self.correspondence:
                    value = prefill_data.pop(key)
                    prefill_data[self.correspondence[key]] = value
        # Show new card type widget.
        card_type_name = unicode(self.card_types_widget.currentText())
        self.card_type = self.card_type_by_name[card_type_name]
        try:                                                                    
            self.card_type_widget = self.component_manager.current\
                    ("card_type_widget", used_for=self.card_type.__class__)\
                          (self.component_manager, parent=self)
        except:
            if not self.card_type_widget:
                self.card_type_widget = self.component_manager.current\
                    ("generic_card_type_widget")(self.component_manager,
                        parent=self, card_type=self.card_type)
        self.card_type_widget.set_data(prefill_data)
        self.card_type_widget.show()
        self.vbox_layout.insertWidget(1, self.card_type_widget)

    def update_tags_combobox(self, current_tag_name):
        self.tags.clear()
        tag_names = sorted([tag.name for tag in self.database().tags() \
            if tag.name != "__UNTAGGED__"], cmp=numeric_string_cmp)
        for name in tag_names:
            self.tags.addItem(name)
        # For the 'special' tags, we add them at the top.
        self.tags.setInsertPolicy(QtGui.QComboBox.InsertAtTop)
        if "," in current_tag_name:
            self.tags.addItem(current_tag_name)
        if current_tag_name == "":
            self.tags.addItem(current_tag_name)
        for i in range(self.tags.count()):
            if self.tags.itemText(i) == current_tag_name:
                self.tags.setCurrentIndex(i)
                break

    def card_type_changed(self, new_card_type_name):
        new_card_type_name = unicode(new_card_type_name)
        self.config()["card_type_name_of_last_added"] = new_card_type_name
        new_card_type = self.card_type_by_name[new_card_type_name]
        if self.card_type.keys().issubset(new_card_type.keys()) or \
               not self.card_type_widget.contains_data():
            self.update_card_widget()            
            return
        dlg = ConvertCardTypeFieldsDlg(self.card_type, new_card_type,
                                       self.correspondence, self)
        if dlg.exec_() == 0:  # Reject.
            self.card_types_widget.setCurrentIndex(self.card_type_index)
            return
        else:          
            self.update_card_widget()

    def preview(self):
        fact_data = self.card_type_widget.data()
        fact = Fact(fact_data)
        cards = self.card_type.create_related_cards(fact)
        tag_text = self.tags.currentText()
        dlg = PreviewCardsDlg(cards, tag_text, self)
        dlg.exec_()

    def __del__(self):
        # Make sure that Python knows Qt has deleted this widget.
        self.card_type_widget = None


class AddCardsDlg(QtGui.QDialog, Ui_AddCardsDlg, AddEditCards, AddCardsDialog):

    def __init__(self, component_manager):
        AddEditCards.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.initialise_card_types_combobox(\
            self.config()["card_type_name_of_last_added"])
        self.update_tags_combobox(\
            self.config()["tags_of_last_added"])  
        self.grades = QtGui.QButtonGroup()
        # Negative indices have special meanings in Qt, so we can't use -1 for
        # 'yet to learn'.
        self.grades.addButton(self.yet_to_learn_button, 0)
        self.grades.addButton(self.grade_2_button, 2)
        self.grades.addButton(self.grade_3_button, 3)
        self.grades.addButton(self.grade_4_button, 4)
        self.grades.addButton(self.grade_5_button, 5)
        self.grades.buttonClicked[int].connect(self.new_cards)
        self.set_valid(False)
        width, height = self.config()["add_widget_size"]
        if width:
            self.resize(width, height)
            
    def closeEvent(self, event):
        self.config()["add_widget_size"] = (self.width(), self.height())
        
    def accept(self):
        self.config()["add_widget_size"] = (self.width(), self.height())
        return QtGui.QDialog.accept(self)
    
    def set_valid(self, valid):
        self.grade_buttons.setEnabled(valid)
        self.preview_button.setEnabled(valid)
        
    def new_cards(self, grade):
        if grade == 0:
            grade = -1
        fact_data = self.card_type_widget.data()
        tag_names = [c.strip() for c in \
                     unicode(self.tags.currentText()).split(',')]
        card_type_name = unicode(self.card_types_widget.currentText())
        card_type = self.card_type_by_name[card_type_name]
        c = self.controller()
        c.create_new_cards(fact_data, card_type, grade, tag_names, save=True)
        tag_text = ", ".join(tag_names)
        self.update_tags_combobox(tag_text)
        self.config()["tags_of_last_added"] = tag_text
        self.card_type_widget.clear()

    def reject(self):
        self.config()["add_widget_size"] = (self.width(), self.height())
        if self.card_type_widget.contains_data():
            status = QtGui.QMessageBox.warning(None, _("Mnemosyne"),
                _("Abandon current card?"), _("&Yes"), _("&No"), "", 1, -1)
            if status == 0:
                QtGui.QDialog.reject(self)
                return
        else:
            QtGui.QDialog.reject(self)
