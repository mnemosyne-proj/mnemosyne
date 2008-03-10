##############################################################################
#
# Two sided card <Peter.Bienstman@UGent.be>
#
##############################################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from card_twosided import *

from libmnemosyne import *
from libmnemosyne.two_sided_card_type import *

##############################################################################
#
# CardTwoSidedDlg # todo: rename to widget
#
##############################################################################

class CardTwoSidedDlg(QWidget, Ui_CardTwoSided):
    
    def __init__(self, parent = None):
        
        QWidget.__init__(self, parent)
        self.setupUi(self)



##############################################################################
#
# register card type
#
##############################################################################

register_card_type("Two-sided card", CardTwoSidedDlg, new_cards_two_sided,
                   update_cards_two_sided))


