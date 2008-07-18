##############################################################################
#
# Three sided card widget <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_card_threesided_wdgt import *

from mnemosyne.libmnemosyne.card_type import *

# TODO: this instantiates the card type, wich should happen elsewhere.

import mnemosyne.libmnemosyne.card_types.three_sided

##############################################################################
#
# CardThreeSidedWdgt
#
##############################################################################

class CardThreeSidedWdgt(QWidget, Ui_CardThreeSidedWdgt):
    
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

        w = unicode(self.foreign_word .document().toPlainText())
        p = unicode(self.pronunciation.document().toPlainText())
        t = unicode(self.translation  .document().toPlainText())
        
        recognition = self.recognition.isChecked()        
        production  = self.production .isChecked()

        # Check if sufficient data is present.

        if recognition and not production:
            if not w:
                return

        if production and not recognition:
            if not t:
                return

        if production and recognition:
            if not w and not t:
                return

        # Return the data.
        
        return {'w' : w, 'p' : p, 't' : t,
                'recognition' : recognition,
                'production'  : production} 



    ##########################################################################
    #
    # clear
    #
    ##########################################################################
    
    def clear(self):

        # TODO: save vice versa settings
        
        self.foreign_word.setText("")
        self.pronunciation.setText("")        
        self.translation.setText("")
        


##############################################################################
#
# Register card type.
#
##############################################################################

# TODO: make sure this only runs once.
# TODO: cleaner way than having to know the correct id.

get_card_type_by_id(2).set_widget_class(CardThreeSidedWdgt)



