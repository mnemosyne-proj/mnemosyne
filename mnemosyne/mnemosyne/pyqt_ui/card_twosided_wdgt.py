##############################################################################
#
# Two sided card widget <Peter.Bienstman@UGent.be>
#
##############################################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_card_twosided_wdgt import *

from mnemosyne.libmnemosyne import *
from mnemosyne.libmnemosyne.card_type import * # TODO: merge
from mnemosyne.libmnemosyne.card_types.two_sided import *

##############################################################################
#
# CardTwoSidedWdgt
#
##############################################################################

class CardTwoSidedWdgt(QWidget, Ui_CardTwoSidedWdgt):
    
    def __init__(self, parent = None):
        
        QWidget.__init__(self, parent)
        self.setupUi(self)

    def get_data(self):
        return "<q>" + self.question.document().toPlainText() + "</q>" + \
               "<a>" + self.answer  .document().toPlainText() + "</a>"



##############################################################################
#
# register card type
#
##############################################################################

register_card_type("Two-sided card", CardTwoSidedWdgt, new_cards_two_sided,
                   update_cards_two_sided)


