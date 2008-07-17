##############################################################################
#
# Configuration widget <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from mnemosyne.core import *
from config_frm import *
from mnemosyne.core.mnemosyne_log import *



##############################################################################
#
# ConfigurationDlg
#
##############################################################################

class ConfigurationDlg(ConfigurationFrm):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent=None, name=None, modal=0, fl=0):
        
        ConfigurationFrm.__init__(self,parent,name,modal,fl)

        QToolTip.setWakeUpDelay(600)
        
        self.font_increase.setValue( \
            get_config("non_latin_font_size_increase"))
        
        self.uploadLogs.setChecked(get_config("upload_logs"))
                
        self.checkDuplicates.setChecked( \
            get_config("check_duplicates_when_adding"))
        self.duplicatesCats.setChecked( \
            get_config("allow_duplicates_in_diff_cat"))

        self.grade_0_items.setValue( \
            get_config("grade_0_items_at_once"))
        self.randomise.setChecked( \
            get_config("randomise_new_cards"))
        
        self.connect(self.button_QA_font, SIGNAL("clicked()"),
                     self.QA_font)
        self.connect(self.button_list_font, SIGNAL("clicked()"),
                     self.list_font)         
        self.connect(self.button_defaults, SIGNAL("clicked()"),
                     self.defaults)
        self.connect(self.button_ok, SIGNAL("clicked()"),
                     self.apply)
        
    ##########################################################################
    #
    # QA_font
    #
    ##########################################################################
    
    def QA_font(self):

        current_font = self.button_ok.font()
        
        if get_config("QA_font") != None:
            current_font.fromString(get_config("QA_font"))

        font, ok = QFontDialog.getFont(current_font)
        if ok == True:         
            set_config("QA_font", unicode(font.toString()))
            
    ##########################################################################
    #
    # list_font
    #
    ##########################################################################
    
    def list_font(self):
        
        current_font = self.button_ok.font()
        
        if get_config("list_font") != None:
            current_font.fromString(get_config("list_font"))

        font, ok = QFontDialog.getFont(current_font)
        if ok == True:         
            set_config("list_font", unicode(font.toString()))
            
    ##########################################################################
    #
    # defaults
    #
    ##########################################################################
    
    def defaults(self):
        
        set_config("QA_font",   None)        
        set_config("list_font", None)
        
        self.uploadLogs     .setChecked(True)
        self.checkDuplicates.setChecked(True)
        self.duplicatesCats .setChecked(True)

        self.font_increase.setValue(0)
        self.grade_0_items.setValue(5)
        
    ##########################################################################
    #
    # apply
    #
    ##########################################################################

    def apply(self):

        set_config("upload_logs",   self.uploadLogs.isOn())
        set_config("check_duplicates_when_adding",self.checkDuplicates.isOn())
        set_config("allow_duplicates_in_diff_cat",self.duplicatesCats.isOn())
        set_config("grade_0_items_at_once", self.grade_0_items.value())
        set_config("randomise_new_cards",self.randomise.isOn())
        set_config("non_latin_font_size_increase", self.font_increase.value())
        
        update_logging_status()             
        
        self.close()
        
