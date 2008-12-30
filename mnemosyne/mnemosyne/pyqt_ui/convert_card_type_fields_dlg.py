#
# convert_card_type_fields_dlg.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_convert_card_type_fields_dlg import Ui_ConvertCardTypeFieldsDlg


class ConvertCardTypeFieldsDlg(QDialog, Ui_ConvertCardTypeFieldsDlg):

    def __init__(self, old_card_type, new_card_type, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.comboboxes = {}

        index = 1
        for fact_key, fact_key_name in old_card_type.fields:
            label = QLabel(self)
            label.setText(fact_key_name + ":")
            font = QFont()
            font.setWeight(50)
            font.setBold(False)
            label.setFont(font)
            self.gridLayout.addWidget(label, index, 0, 1, 1)
        
            combobox = QComboBox(self)
            for new_fact_key, new_key_name in new_card_type.fields:
                combobox.addItem(new_key_name)
            self.gridLayout.addWidget(combobox, index, 1, 1, 1)

            self.comboboxes[fact_key] = combobox
            
            index += 1

    def accept(self):
        print "hi"
        
