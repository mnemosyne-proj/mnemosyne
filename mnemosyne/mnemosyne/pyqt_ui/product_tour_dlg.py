##############################################################################
#
# Product tour widget <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from mnemosyne.core import *
from product_tour_frm import *
from mnemosyne.core.mnemosyne_log import *



##############################################################################
#
# ProductTourDlg
#
##############################################################################

class ProductTourDlg(ProductTourFrm):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent=None, name=None, modal=0, fl=0):
        
        ProductTourFrm.__init__(self,parent,name,modal,fl)

        for i in range(self.pageCount()):
            self.setHelpEnabled(self.page(i),False)

        self.setFinishEnabled(self.page(self.pageCount()-1),True)  
        
    ##########################################################################
    #
    # accept
    #
    ##########################################################################

    def accept(self):

        set_config("upload_logs", self.uploadLogs.isOn())

        update_logging_status()             
        
        self.close()
