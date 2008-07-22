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

from mnemosyne.libmnemosyne.plugin_manager import plugin_manager
from mnemosyne.libmnemosyne.card_types.three_sided import ThreeSided



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

        f = unicode(self.foreign_word .document().toPlainText())
        p = unicode(self.pronunciation.document().toPlainText())
        t = unicode(self.translation  .document().toPlainText())
        
        recognition = self.recognition.isChecked()        
        production  = self.production .isChecked()

        # Check if sufficient data is present.

        if recognition and not production:
            if not f:
                return

        if production and not recognition:
            if not t:
                return

        if production and recognition:
            if not f and not t:
                return

        # Return the data.
        
        return {'f' : f, 'p' : p, 't' : t,
                'recognition' : recognition,
                'production'  : production} 



    ##########################################################################
    #
    # clear
    #
    ##########################################################################
    
    def clear(self):

        # TODO: save vice versa settings.
        
        self.foreign_word.setText("")
        self.pronunciation.setText("")        
        self.translation.setText("")
        


##############################################################################
#
# Register card type.
#
##############################################################################

print "Registering three sided card type."

c = ThreeSided()
c.widget_class = CardThreeSidedWdgt
plugin_manager.register_plugin("card_type", c)

    



