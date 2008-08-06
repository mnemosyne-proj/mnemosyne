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
        
        return {'q' : q, 'a' : a} 



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
# Register card type widget.
#
##############################################################################

print "Registering two sided card widget type."

#component_manager.register("card_type_widget", CardTwoSidedWdgt,
#                           used_for="BothWays")

