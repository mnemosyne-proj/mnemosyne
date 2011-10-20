#
# card_appearance_dlg.py <Peter.Bienstman@UGent.be>
#

from copy import deepcopy

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
from mnemosyne.pyqt_ui.ui_card_appearance_dlg import Ui_CardAppearanceDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import CardAppearanceDialog


class CardAppearanceDlg(QtGui.QDialog, Ui_CardAppearanceDlg,
                        CardAppearanceDialog):

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.dynamic_widgets = []
        self.affected_card_types = []
        self.fact_key_names = []
        self.non_latin_font_size_increase.setValue\
            (self.config()['non_latin_font_size_increase'])
        # We calculate card_type_by_name here because these names can change
        # if the user chooses another translation.
        self.card_types_widget.addItem(_("<all card types>"))
        self.card_type_by_name = {}
        for card_type in self.card_types():
            self.card_type_by_name[_(card_type.name)] = card_type
            self.card_types_widget.addItem(_(card_type.name))          
        # Store backups in order to be able to revert our changes.
        self.old_font = deepcopy(self.config()["font"])
        self.old_background_colour = \
            deepcopy(self.config()["background_colour"])
        self.old_font_colour = deepcopy(self.config()["font_colour"])
        self.old_alignment = deepcopy(self.config()["alignment"])
        self.changed = False
        
    def activate(self):
        self.exec_()
        
    def card_type_changed(self, new_card_type_name):
        if new_card_type_name == _("<all card types>"):
            self.affected_card_types = self.card_types()
            self.fact_key_names = [_("Text")]
            for widget in [self.label_non_latin_1, self.label_non_latin_2,
                self.label_non_latin_3, self.line_non_latin,
                self.non_latin_font_size_increase]:
                widget.show()
        else:
            new_card_type_name = unicode(new_card_type_name)
            new_card_type = self.card_type_by_name[new_card_type_name]
            self.affected_card_types = [new_card_type]
            self.fact_key_names = new_card_type.fact_key_names()
            for widget in [self.label_non_latin_1, self.label_non_latin_2,
                self.label_non_latin_3, self.line_non_latin,
                self.non_latin_font_size_increase]:
                widget.hide()
        for widget in self.dynamic_widgets:
            self.gridLayout.removeWidget(widget)
            widget.close()
        self.dynamic_widgets = []
        
        row = 0
        self.font_buttons = QtGui.QButtonGroup()
        self.colour_buttons = QtGui.QButtonGroup()
        self.align_buttons = QtGui.QButtonGroup()
        self.align_buttons.setExclusive(False)
        for key_name in self.fact_key_names:
            label = QtGui.QLabel(_(key_name) + ":", self)
            self.gridLayout.addWidget(label, row, 0, 1, 1)
            self.dynamic_widgets.append(label)
            
            font = QtGui.QPushButton(_("Select font"), self)
            self.font_buttons.addButton(font, row)
            self.gridLayout.addWidget(font, row, 1, 1, 1)
            self.dynamic_widgets.append(font)
            
            colour = QtGui.QPushButton(_("Select colour"),self)
            self.colour_buttons.addButton(colour, row)
            self.gridLayout.addWidget(colour, row, 2, 1, 1)
            self.dynamic_widgets.append(colour)
            
            row += 1
        self.gridLayout.setColumnStretch(1, 10)
        self.gridLayout.setColumnStretch(2, 10)
        self.font_buttons.buttonClicked[int].connect(self.update_font)
        self.colour_buttons.buttonClicked[int].\
            connect(self.update_font_colour)
        
        try:
            current_alignment = self.config()["alignment"]\
                                [self.affected_card_types[0].id]
        except:
            current_alignment = "center"
        if current_alignment == "left":
            self.alignment.setCurrentIndex(0)
        elif current_alignment == "center":
            self.alignment.setCurrentIndex(1)
        elif current_alignment == "right":
            self.alignment.setCurrentIndex(2)
        # Make font light if different alignments are active.
        self.alignment.setFont(self.font())
        values = set()
        for card_type in self.affected_card_types:
            if not card_type.id in self.config()["alignment"]:
                values.add("center")
            else:
                values.add(self.config()["alignment"][card_type.id])
        if len(values) > 1:
            self.alignment.font().setWeight(25)
        else:
            self.alignment.font().setWeight(50)            
        self.adjustSize()

    def update_background_colour(self):
        # Determine current colour.
        current_rgb = self.config().card_type_property("background_colour",
            self.affected_card_types[0])
        if current_rgb:
            current_colour = QtGui.QColor(current_rgb)
        else:
            current_colour = QtGui.QColor(QtCore.Qt.white)
        # Set new colour.
        colour = QtGui.QColorDialog.getColor(current_colour, self)
        if colour.isValid():
            for card_type in self.affected_card_types:
                self.config().set_card_type_property("background_colour",
                    colour.rgb(), card_type)
            self.changed = True
        
    def update_font(self, index):
        # Determine keys affected.
        if len(self.affected_card_types) > 1:
            affected_fact_key = None # Actually means all the keys.
        else:
            affected_fact_key = \
                self.affected_card_types[0].fact_keys_and_names[index][0]          
        # Determine current font.
        if len(self.affected_card_types) > 1:
            font_string = self.config().card_type_property(\
                "font", self.card_type_with_id("1"), "f")
        else:
            font_string = self.config().card_type_property(\
                "font", self.affected_card_types[0], affected_fact_key)
        current_font = QtGui.QFont(self.font()) 
        if font_string:
            current_font.fromString(font_string)
        # Set new font.
        font, ok = QtGui.QFontDialog.getFont(current_font, self)
        if ok:
            font_string = unicode(font.toString())
            for card_type in self.affected_card_types:
                self.config().set_card_type_property("font", font_string,
                    card_type, affected_fact_key)
            self.changed = True
        
    def update_font_colour(self, index):
        # Determine keys affected.
        if len(self.affected_card_types) > 1:
            affected_fact_key = None # Actually means all the keys.
        else:
            affected_fact_key = \
                self.affected_card_types[0].fact_keys_and_names[index][0]            
        # Determine current colour.
        if len(self.affected_card_types) > 1:
            current_rgb = self.config().card_type_property(\
                "font_colour", self.card_type_with_id("1"), "f")
        else:
            current_rgb = self.config().card_type_property(\
                "font_colour", self.affected_card_types[0], affected_fact_key)
        if current_rgb:
            current_colour = QtGui.QColor(current_rgb)
        else:
            current_colour = QtGui.QColor(QtCore.Qt.black)
        # Set new colour.
        colour = QtGui.QColorDialog.getColor(current_colour, self)
        if colour.isValid():
            for card_type in self.affected_card_types:
                self.config().set_card_type_property("font_colour",
                    colour.rgb(), card_type, affected_fact_key)
            self.changed = True
        
    def update_alignment(self, index):
        if index == 0:
            new_alignment = "left"
        elif index == 1:
            new_alignment = "center"
        elif index == 2:
            new_alignment = "right"                
        for card_type in self.affected_card_types:
            self.config().set_card_type_property("alignment", new_alignment,
                card_type)
        self.alignment.font().setWeight(50)
        self.changed = True
        
    def accept(self):
        self.config()["non_latin_font_size_increase"] = \
            self.non_latin_font_size_increase.value()
        for card_type in self.card_types():
            for render_chain in self.component_manager.all("render_chain"):
                render_chain.renderer_for_card_type(card_type).\
                    update(card_type)
        QtGui.QDialog.accept(self)     
        
    def preview(self):
        card_type = self.affected_card_types[0]
        for render_chain in self.component_manager.all("render_chain"):
            render_chain.renderer_for_card_type(card_type).update(card_type)
        fact_data = {}
        for fact_key, fact_key_name in card_type.fact_keys_and_names:
            fact_data[fact_key] = _(fact_key_name)
        fact = Fact(fact_data)
        cards = card_type.create_sister_cards(fact)        
        tag_text = ""
        dlg = PreviewCardsDlg(self.component_manager, cards, tag_text, self)
        dlg.exec_()
        
    def defaults(self):
        if len(self.affected_card_types) > 1:
            message = _("Reset all card types to default?")
        else:
            message = _("Reset '%s' to default?") \
                % (_(self.affected_card_types[0].name))
        result = QtGui.QMessageBox.question(None, _("Mnemosyne"), message,
            _("&Yes"), _("&No"), "", 0, -1)
        if result == 1:
            return
        self.non_latin_font_size_increase.setValue(0)
        if len(self.affected_card_types) > 1:        
            self.config()["font"] = {}
            self.config()["background_colour"] = {}
            self.config()["font_colour"] = {}
            self.config()["alignment"] = {}
        else:
            card_type_id = self.affected_card_types[0].id
            self.config()["font"].pop(card_type_id, None)
            self.config()["background_colour"].pop(card_type_id, None)
            self.config()["font_colour"].pop(card_type_id, None)
            self.config()["alignment"].pop(card_type_id, None)
        self.alignment.setCurrentIndex(1)

    def reject(self):
        if self.changed == True:
            result = QtGui.QMessageBox.question(None, _("Mnemosyne"),
                _("Abandon changes?"), _("&Yes"), _("&No"), "", 0, -1)
            if result == 1:
                return
        self.config()["font"] = self.old_font
        self.config()["background_colour"] = self.old_background_colour
        self.config()["font_colour"] = self.old_font_colour
        self.config()["alignment"] = self.old_alignment
        for card_type in self.card_types():
            for render_chain in self.component_manager.all("render_chain"):
                render_chain.renderer_for_card_type(card_type).\
                    update(card_type)        
        QtGui.QDialog.reject(self)   
