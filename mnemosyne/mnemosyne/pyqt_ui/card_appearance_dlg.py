#
# card_appearance_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from copy import deepcopy

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_card_appearance_dlg import Ui_CardAppearanceDlg

from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.component_manager import config, card_types
from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg


class CardAppearanceDlg(QDialog, Ui_CardAppearanceDlg):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.dynamic_widgets = []
        self.affected_card_types = []
        self.key_names = []
        
        # We calculate card_type_by_name here rather than in the component
        # manager, because these names can change if the user chooses another
        # translation.
        self.card_types.addItem(_("<all card types>"))
        self.card_type_by_name = {}
        for card_type in card_types():
            self.card_type_by_name[card_type.name] = card_type
            self.card_types.addItem(card_type.name)
            
        # Store backups in order to be able to revert our changes.
        self.old_font = deepcopy(config()["font"])
        self.old_background_colour = deepcopy(config()["background_colour"])
        self.old_font_colour = deepcopy(config()["font_colour"])
        self.old_alignment = deepcopy(config()["alignment"])
        self.changed = False

    def card_type_changed(self, new_card_type_name):
        if new_card_type_name == _("<all card types>"):
            self.affected_card_types = card_types()
            self.key_names = ["Text"]
        else:
            new_card_type_name = unicode(new_card_type_name)
            new_card_type = self.card_type_by_name[new_card_type_name]
            self.affected_card_types = [new_card_type]
            self.key_names = new_card_type.key_names()

        for widget in self.dynamic_widgets:
            self.gridLayout.removeWidget(widget)
            widget.close()
        self.dynamic_widgets = []

        row = 2
        self.font_buttons = QButtonGroup()
        self.colour_buttons = QButtonGroup()
        self.align_buttons = QButtonGroup()
        for key_name in self.key_names:
            label = QLabel(key_name + ":", self)
            self.gridLayout.addWidget(label, row, 0, 1, 1)
            self.dynamic_widgets.append(label)
            
            font = QPushButton(_("Font"), self)
            self.font_buttons.addButton(font, row-2)
            self.gridLayout.addWidget(font, row, 1, 1, 1)
            self.dynamic_widgets.append(font)
            
            colour = QPushButton(_("Colour"),self)
            self.colour_buttons.addButton(colour, row-2)
            self.gridLayout.addWidget(colour, row, 2, 1, 1)
            self.dynamic_widgets.append(colour)
            
            left_align = QCheckBox(_("Left align"), self)
            self.align_buttons.addButton(left_align, row-2)
            self.gridLayout.addWidget(left_align, row, 3, 1, 1)
            self.dynamic_widgets.append(left_align)
            
            row += 1
            
        self.connect(self.font_buttons, SIGNAL("buttonClicked(int)"),
                     self.update_font)
        self.connect(self.colour_buttons, SIGNAL("buttonClicked(int)"),
                     self.update_font_colour)
        self.connect(self.align_buttons, SIGNAL("buttonClicked(int)"),
                     self.update_align)

    def update_background_colour(self):
        # Determine current colour.
        current_colour = Qt.black
        if 1:
            current_rgb = config()["background_colour"]\
                          [self.affected_card_types[0].id]
            current_colour = QColor(current_rgb)
        else:
            pass
        
        # Set new colour.
        colour = QColorDialog.getColor(current_colour, self)
        if colour.isValid():
            for card_type in self.affected_card_types:
                card_type.get_renderer().set_property("background_colour",
                                                      colour.rgb(), card_type)
            self.changed = True
        
    def update_font(self, index):
        # Determine keys affected.
        if len(self.affected_card_types) > 1:
            affected_key = None # Actually means all the keys.
        else:
            affected_key = self.affected_card_types[0].fields[index][0]
            
        # Determine current font.
        current_font = QFont(self.font())
        try:
            if len(self.affected_card_types) > 1:
                font_string = config()['font']['1']['q']
            else:
                font_string = config()['font'][self.affected_card_types[0].id]\
                                                             [affected_key]
            current_font.fromString(font_string)
        except:
            pass
        
        # Set new font.
        font, ok = QFontDialog.getFont(current_font, self)
        if ok:
            font_string = unicode(font.toString())
            for card_type in self.affected_card_types:
                card_type.get_renderer().set_property('font', font_string,
                                                      card_type, affected_key)
            self.changed = True
        
    def update_font_colour(self, index):
        # Determine keys affected.
        if len(self.affected_card_types) > 1:
            affected_key = None # Actually means all the keys.
        else:
            affected_key = self.affected_card_types[0].fields[index][0]
            
        # Determine current colour.
        current_colour = Qt.black
        try:
            if len(self.affected_card_types) > 1:
                current_rgb = config()['font_colour']['1']['q']
            else:
                current_rgb = config()['font_colour']\
                             [self.affected_card_types[0].id][affected_key]
            current_colour = QColor(current_rgb)
        except:
            pass
        
        # Set new colour.
        colour = QColorDialog.getColor(current_colour, self)
        if colour.isValid():
            for card_type in self.affected_card_types:
                card_type.get_renderer().set_property('font_colour', colour.rgb(),
                                                      card_type, affected_key)
            self.changed = True
        
    def update_align(self, index):
        print 'updated align', index
        self.changed = True
        
    def accept(self):
        for card_type in self.affected_card_types:
            card_type.get_renderer().update(card_type)
        QDialog.accept(self)     
        
    def preview(self):
        card_type = self.affected_card_types[0]
        card_type.get_renderer().update(card_type)
        fact_data = {}
        for fact_key, fact_key_name in card_type.fields:
            fact_data[fact_key] = fact_key_name
        fact = Fact(fact_data, card_type)
        cards = card_type.create_related_cards(fact)        
        cat_text = ""
        dlg = PreviewCardsDlg(cards, cat_text, self)
        dlg.exec_()
        
    def defaults(self):
        config()["font"] = {}
        config()["background_colour"] = {}
        config()["font_colour"] = {}
        config()["alignment"] = {}

    def reject(self):
        if self.changed == True:
            result = QMessageBox.question(None, _("Mnemosyne"), _("Abandon changes?"),
                                          _("&Yes"), _("&No"), "", 0, -1)
            if result == 1:
                return
        config()["font"] = self.old_font
        config()["background_colour"] = self.old_background_colour
        config()["font_colour"] = self.old_font_colour
        config()["alignment"] = self.old_alignment
        QDialog.reject(self)   
