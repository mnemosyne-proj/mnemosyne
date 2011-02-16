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
        self.dynamic_widgets = []
        self.affected_card_types = []
        self.key_names = []       
        # We calculate card_type_by_name here because these names can change
        # if the user chooses another translation.
        self.card_types_widget.addItem(_("<all card types>"))
        self.card_type_by_name = {}
        for card_type in self.card_types():
            self.card_type_by_name[card_type.name] = card_type
            self.card_types_widget.addItem(card_type.name)          
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
            self.key_names = [_("Text")]
        else:
            new_card_type_name = unicode(new_card_type_name)
            new_card_type = self.card_type_by_name[new_card_type_name]
            self.affected_card_types = [new_card_type]
            self.key_names = new_card_type.key_names()

        for widget in self.dynamic_widgets:
            self.gridLayout.removeWidget(widget)
            widget.close()
        self.dynamic_widgets = []

        row = 0
        self.font_buttons = QtGui.QButtonGroup()
        self.colour_buttons = QtGui.QButtonGroup()
        self.align_buttons = QtGui.QButtonGroup()
        self.align_buttons.setExclusive(False)
        for key_name in self.key_names:
            label = QtGui.QLabel(key_name + ":", self)
            self.gridLayout.addWidget(label, row, 0, 1, 1)
            self.dynamic_widgets.append(label)
            
            font = QtGui.QPushButton(_("Set font"), self)
            self.font_buttons.addButton(font, row)
            self.gridLayout.addWidget(font, row, 1, 1, 1)
            self.dynamic_widgets.append(font)
            
            colour = QtGui.QPushButton(_("Set colour"),self)
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
        current_colour = QtGui.QColor(QtCore.Qt.white)
        try:
            current_rgb = self.config()["background_colour"]\
                          [self.affected_card_types[0].id]
            current_colour = QtGui.QColor(current_rgb)
        except:
            pass       
        # Set new colour.
        colour = QtGui.QColorDialog.getColor(current_colour, self)
        if colour.isValid():
            for card_type in self.affected_card_types:
                self.config().set_appearance_property("background_colour",
                    colour.rgb(), card_type)
            self.changed = True
        
    def update_font(self, index):
        # Determine keys affected.
        if len(self.affected_card_types) > 1:
            affected_key = None # Actually means all the keys.
        else:
            affected_key = self.affected_card_types[0].fields[index][0]          
        # Determine current font.
        current_font = QtGui.QFont(self.font())
        try:
            if len(self.affected_card_types) > 1:
                font_string = self.config()["font"]["1"]["q"]
            else:
                font_string = self.config()["font"]\
                    [self.affected_card_types[0].id][affected_key]
            current_font.fromString(font_string)
        except:
            pass        
        # Set new font.
        font, ok = QtGui.QFontDialog.getFont(current_font, self)
        if ok:
            font_string = unicode(font.toString())
            for card_type in self.affected_card_types:
                self.config().set_appearance_property("font", font_string,
                    card_type, affected_key)
            self.changed = True
        
    def update_font_colour(self, index):
        # Determine keys affected.
        if len(self.affected_card_types) > 1:
            affected_key = None # Actually means all the keys.
        else:
            affected_key = self.affected_card_types[0].fields[index][0]            
        # Determine current colour.
        current_colour = QtGui.QColor(QtCore.Qt.black)
        try:
            if len(self.affected_card_types) > 1:
                current_rgb = self.config()["font_colour"]["1"]["q"]
            else:
                current_rgb = self.config()["font_colour"]\
                             [self.affected_card_types[0].id][affected_key]
            current_colour = QtGui.QColor(current_rgb)
        except:
            pass
        # Set new colour.
        colour = QtGui.QColorDialog.getColor(current_colour, self)
        if colour.isValid():
            for card_type in self.affected_card_types:
                self.config().set_appearance_property("font_colour",
                    colour.rgb(), card_type, affected_key)
            self.changed = True
        
    def update_alignment(self, index):
        if index == 0:
            new_alignment = "left"
        elif index == 1:
            new_alignment = "center"
        elif index == 2:
            new_alignment = "right"                
        for card_type in self.affected_card_types:
            self.config().set_appearance_property("alignment", new_alignment,
                card_type)
        self.alignment.font().setWeight(50)
        self.changed = True
        
    def accept(self):
        for card_type in self.affected_card_types:
            for render_chain in self.component_manager.all("render_chain"):
                render_chain.renderer_for_card_type(card_type).\
                    update(card_type)
        QtGui.QDialog.accept(self)     
        
    def preview(self):
        card_type = self.affected_card_types[0]
        for render_chain in self.component_manager.all("render_chain"):
            render_chain.renderer_for_card_type(card_type).update(card_type)
        fact_data = {}
        for fact_key, fact_key_name, language_code in card_type.fields:
            fact_data[fact_key] = fact_key_name
        fact = Fact(fact_data)
        cards = card_type.create_sister_cards(fact)        
        tag_text = ""
        dlg = PreviewCardsDlg(cards, tag_text, self)
        dlg.exec_()
        
    def defaults(self):
        self.config()["font"] = {}
        self.config()["background_colour"] = {}
        self.config()["font_colour"] = {}
        self.config()["alignment"] = {}
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