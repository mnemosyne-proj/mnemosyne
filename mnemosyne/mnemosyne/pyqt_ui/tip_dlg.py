##############################################################################
#
# Tip of the day dialog <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from tip_frm import *
from mnemosyne.core import *


##############################################################################
#
# TipDlg
#
##############################################################################

class TipDlg(TipFrm):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent=None, name=None, modal=0, fl=0):
        
        TipFrm.__init__(self,parent,name,modal,fl)

        self.show_tips.setChecked(get_config("show_daily_tips"))
        
        self.tips = []

        self.tips.append(self.trUtf8("Tip 1"))
        self.tips.append(self.trUtf8("Tip 2"))
        self.tips.append(self.trUtf8("Tip 3"))

        self.update_dialog()
        
    ##########################################################################
    #
    # update_dialog
    #
    ##########################################################################
    
    def update_dialog(self):
        
        tip = get_config("tip")
        self.tip_label.setText(self.tips[tip])
        self.previous_button.setEnabled(tip != 0)
        self.next_button.setEnabled(tip != len(self.tips)-1)
        
    ##########################################################################
    #
    # previous
    #
    ##########################################################################
    
    def previous(self):
        
        set_config("tip", (get_config("tip")-1) % len(self.tips))
        self.update_dialog()

    ##########################################################################
    #
    # next
    #
    ##########################################################################
    
    def next(self):
        
        set_config("tip", (get_config("tip")+1) % len(self.tips))
        self.update_dialog()

    ##########################################################################
    #
    # closeEvent
    #
    ##########################################################################

    def closeEvent(self, event):
        
        set_config("show_daily_tips",self.show_tips.isOn())
        set_config("tip", (get_config("tip")+1) % len(self.tips))
        event.accept()
