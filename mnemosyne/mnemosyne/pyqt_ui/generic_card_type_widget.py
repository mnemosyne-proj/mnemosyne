#
# generic_card_type_widget.py <Peter.Bienstman@UGent.be>
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from mnemosyne.pyqt_ui.qtextedit2 import QTextEdit2
from mnemosyne.libmnemosyne.ui_components.card_type_widget \
     import CardTypeWidget

class GenericCardTypeWdgt(QWidget, CardTypeWidget):

    def __init__(self, card_type, parent, component_manager):
        QWidget.__init__(self, parent)
        CardTypeWidget.__init__(self, component_manager)
        self.card_type = card_type
        self.hboxlayout = QHBoxLayout(self)
        self.hboxlayout.setMargin(0)
        self.vboxlayout = QVBoxLayout()
        self.edit_boxes = {}
        self.top_edit_box = None
        for fact_key, fact_key_name in self.card_type.fields:
            self.vboxlayout.addWidget(QLabel(fact_key_name + ":", self))
            t = QTextEdit2(self)
            t.setTabChangesFocus(True)
            t.setUndoRedoEnabled(True)
            t.setReadOnly(False)
            try:
                colour = self.config()["font_colour"][card_type.id][fact_key]
                t.setTextColor(QColor(colour))
            except:
                pass
            try:
                colour = self.config()["background_colour"][card_type.id]
                p = QPalette()
                p.setColor(QPalette.Active, QPalette.Base, QColor(colour))
                t.setPalette(p)
            except:
                pass
            try:
                font_string = self.config()["font"][card_type.id][fact_key]
                font = QFont()
                font.fromString(font_string)
                t.setCurrentFont(font)
            except:
                pass            
            if len(self.card_type.fields) > 2:
                t.setMinimumSize(QSize(0,60))
            else:
                t.setMinimumSize(QSize(0,106))
            self.vboxlayout.addWidget(t)
            self.edit_boxes[t] = fact_key
            if not self.top_edit_box:
                self.top_edit_box = t
            self.connect(t, SIGNAL("textChanged()"), self.text_changed)
        self.hboxlayout.addLayout(self.vboxlayout)
        self.resize(QSize(QRect(0,0,325,264).size()).\
                    expandedTo(self.minimumSizeHint()))

    def contains_data(self):
        for edit_box in self.edit_boxes:
            if unicode(edit_box.document().toPlainText()):
                return True
        return False

    def get_data(self):
        fact_data = {}
        for edit_box, fact_key in self.edit_boxes.iteritems():
            fact_data[fact_key] = unicode(edit_box.document().toPlainText())
        return fact_data

    def set_data(self, data):
        if data:
            for edit_box, fact_key in self.edit_boxes.iteritems():
                if fact_key in data.keys():
                    edit_box.setText(data[fact_key])

    def clear(self):
        for edit_box in self.edit_boxes:
            edit_box.setText("")
        self.top_edit_box.setFocus()
    
    def text_changed(self):
        self.parent().set_valid(self.card_type.is_data_valid(self.get_data()))
