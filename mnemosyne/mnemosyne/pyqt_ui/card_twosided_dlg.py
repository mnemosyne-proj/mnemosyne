##############################################################################
#
# Two sided card <Peter.Bienstman@UGent.be>
#
# TODO: rename
#
##############################################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from card_twosided import *

##############################################################################
#
# CardTwoSidedDlg
#
##############################################################################

class CardTwoSidedDlg(QWidget, Ui_CardTwoSided):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent = None):
        
        QWidget.__init__(self, parent)
        self.setupUi(self)

