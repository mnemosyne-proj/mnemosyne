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

from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.card_types.two_sided import TwoSided



##############################################################################
#
# CardTwoSidedWdgt
#
##############################################################################

class CardTwoSidedWdgt(QWidget, Ui_CardTwoSidedWdgt):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent = None):
        
        QWidget.__init__(self, parent)
        self.setupUi(self)


        
    ##########################################################################
    #
    # get_data
    #
    ##########################################################################
    
    def get_data(self):

        # Get the data from the form.

        q = unicode(self.question.document().toPlainText())
        a = unicode(self.answer  .document().toPlainText())

        # TODO: Check if sufficient data is present.


        # Return the data.
        
        return {'q' : q, 'a' : a, 'add_vice_versa' : add_vice_versa} 



    ##########################################################################
    #
    # clear
    #
    ##########################################################################
    
    def clear(self):

        # TODO: save vice versa settings
        
        self.question.setText("")
        self.answer.setText("")        



##############################################################################
#
# Register card type.
#
##############################################################################

print "Registering two sided card type."

c = TwoSided()
#c.widget_class = CardTwoSidedWdgt
component_manager.register("card_type", c)


component_manager.register("card_type_widget", CardTwoSidedWdgt, "TwoSided")

