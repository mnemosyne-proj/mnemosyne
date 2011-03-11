#
# card_type_wdgt_generic.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.pyqt_ui.qtextedit2 import QTextEdit2
from mnemosyne.libmnemosyne.ui_components.card_type_widget \
     import GenericCardTypeWidget


class GenericCardTypeWdgt(QtGui.QWidget, GenericCardTypeWidget):

    def __init__(self, component_manager, parent, card_type):
        QtGui.QWidget.__init__(self, parent)
        GenericCardTypeWidget.__init__(self, component_manager)
        self.card_type = card_type
        self.hboxlayout = QtGui.QHBoxLayout(self)
        self.hboxlayout.setMargin(0)
        self.vboxlayout = QtGui.QVBoxLayout()
        self.fact_key_for_edit_box = {}
        self.top_edit_box = None
        # Does this card type need to deal with the hiding of pronunciation
        # fields?
        if "p_1" not in self.card_type.keys():
            pronunciation_hiding = None
        else:
            try:
                pronunciation_hiding = self.config()\
                    ["hide_pronunciation_field"][self.card_type.id]["p_1"]
            except KeyError:
                pronunciation_hiding = False
        # Construct the rest of the dialog.
        for fact_key, fact_key_name in self.card_type.fields:
            l = QtGui.QLabel(fact_key_name + ":", self)
            self.vboxlayout.addWidget(l)
            if fact_key == "p_1":
                self.pronunciation_label = l
                self.pronunciation_label.setVisible(not pronunciation_hiding)            
            t = QTextEdit2(self, pronunciation_hiding)
            t.setTabChangesFocus(True)
            t.setUndoRedoEnabled(True)
            t.setReadOnly(False)
            if len(self.card_type.fields) > 2:
                t.setMinimumSize(QtCore.QSize(0, 60))
            else:
                t.setMinimumSize(QtCore.QSize(0, 106))
            self.vboxlayout.addWidget(t)
            self.fact_key_for_edit_box[t] = fact_key
            if not self.top_edit_box:
                self.top_edit_box = t
            if fact_key == "p_1":
                self.pronunciation_box = t
                self.pronunciation_box.setVisible(not pronunciation_hiding)
            self.update_formatting(t)
            t.textChanged.connect(self.text_changed)
            t.currentCharFormatChanged.connect(self.reset_formatting)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.resize(QtCore.QSize(QtCore.QRect(0,0,325,264).size()).\
                    expandedTo(self.minimumSizeHint()))
        self.top_edit_box.setFocus()

    def pronunciation_hiding_toggled(self, checked):
        self.config().set_appearance_property("hide_pronunciation_field",
            checked, self.card_type)
        self.pronunciation_label.setVisible(not checked)
        self.pronunciation_box.setVisible(not checked)
        self.pronunciation_box.pronunciation_hiding = checked
        
    def update_formatting(self, edit_box):
        fact_key = self.fact_key_for_edit_box[edit_box]
        try:
            colour = self.config()["font_colour"][self.card_type.id][fact_key]
            edit_box.setTextColor(QtGui.QColor(colour))
        except KeyError:
            # The defaults have not been changed, there is no key for colour.
            pass
        try:
            colour = self.config()["background_colour"][self.card_type.id]
            p = QtGui.QPalette()
            p.setColor(QtGui.QPalette.Active, QtGui.QPalette.Base,
                       QtGui.QColor(colour))
            edit_box.setPalette(p)
        except KeyError:
            pass
        try:
            font_string = self.config()["font"][self.card_type.id][fact_key]
            font = QtGui.QFont()
            font.fromString(font_string)                
            edit_box.setCurrentFont(font)
        except KeyError:
            pass

    def reset_formatting(self):

        """Deleting all the text reverts back to the system font, so we have
        to force our custom font again.

        """
        
        for edit_box in self.fact_key_for_edit_box:
            self.update_formatting(edit_box)

    def contains_data(self):
        for edit_box in self.fact_key_for_edit_box:
            if unicode(edit_box.document().toPlainText()):
                return True
        return False

    def data(self):
        fact_data = {}
        for edit_box, fact_key in self.fact_key_for_edit_box.iteritems():
            fact_data[fact_key] = unicode(edit_box.document().toPlainText())
        return fact_data

    def set_data(self, data):
        if data:
            for edit_box, fact_key in self.fact_key_for_edit_box.iteritems():
                if fact_key in data.keys():
                    edit_box.setPlainText(data[fact_key])

    def clear(self):
        for edit_box in self.fact_key_for_edit_box:
            edit_box.setText("")
        self.top_edit_box.setFocus()
    
    def text_changed(self):
        self.parent().set_valid(self.card_type.is_data_valid(self.data()))
