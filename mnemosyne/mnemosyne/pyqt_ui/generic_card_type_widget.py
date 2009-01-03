#
# generic_card_type_widget.py <Peter.Bienstman@UGent.be>
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from mnemosyne.pyqt_ui.qtextedit2 import QTextEdit2


class GenericCardTypeWdgt(QWidget):

    def __init__(self, card_type, prefill_data=None, parent=None):
        QWidget.__init__(self, parent)
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
            if len(self.card_type.fields) > 2:
                t.setMinimumSize(QSize(0,60))
            else:
                t.setMinimumSize(QSize(0,106))
            self.vboxlayout.addWidget(t)
            self.edit_boxes[t] = fact_key
            if not self.top_edit_box:
                self.top_edit_box = t
        if prefill_data:
            for edit_box, fact_key in self.edit_boxes.iteritems():
                if fact_key in prefill_data.keys():
                    edit_box.setText(prefill_data[fact_key])
        self.hboxlayout.addLayout(self.vboxlayout)
        self.resize(QSize(QRect(0,0,325,264).size()).\
                    expandedTo(self.minimumSizeHint()))

    def contains_data(self):
        for edit_box in self.edit_boxes:
            if unicode(edit_box.document().toPlainText()):
                return True
        return False

    def get_data(self, check_for_required=True):
        fact = {}
        for edit_box, fact_key in self.edit_boxes.iteritems():
            fact[fact_key] = unicode(edit_box.document().toPlainText())
        if not check_for_required:
            return fact
        for required in self.card_type.required_fields():
            if not fact[required]:
                raise ValueError
        return fact

    def clear(self):
        for edit_box in self.edit_boxes:
            edit_box.setText("")
        self.top_edit_box.setFocus()
