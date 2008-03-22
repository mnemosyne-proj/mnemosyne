##############################################################################
#
# About dialog <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from about_frm import *
import mnemosyne.version


##############################################################################
#
# AboutDlg
#
##############################################################################

class AboutDlg(AboutFrm):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent=None, name=None, modal=0, fl=0):
        
        AboutFrm.__init__(self,parent,name,modal,fl)
        self.about_label.setText(
            self.trUtf8("Mnemosyne").append(" " + \
            mnemosyne.version.version + "\n\n").append(\
            self.trUtf8("Main author: Peter Bienstman\n\n")).append(\
            self.trUtf8("More info: http://mnemosyne-proj.org\n")))
