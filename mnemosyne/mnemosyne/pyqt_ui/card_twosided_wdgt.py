##############################################################################
#
# Two sided card widget <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

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

        # Get the data from the form.

        q = unicode(self.question.document().toPlainText())
        a = unicode(self.answer  .document().toPlainText())
        
        add_vice_versa = self.vice_versa.isChecked()

        # Check if sufficient data is present.

        if add_vice_versa:
            if not q  or not a:
                return
        else:
            if not q:
                return

        # Return the data.
        
        return {'q' : q, 'a' : a, 'add_vice_versa' : add_vice_versa} 



##############################################################################
#
# register card type
#
##############################################################################

register_card_type(_("Regular card"), CardTwoSidedWdgt, new_cards_two_sided,
                   update_cards_two_sided)


