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

        self.leftAlign .setChecked(get_config("left_align"))
        self.keepLogs  .setChecked(get_config("keep_logs"))
        self.uploadLogs.setChecked(get_config("upload_logs"))
        
        self.uploadServer.setText(get_config("upload_server"))
        
        self.checkDuplicates.setChecked( \
            get_config("check_duplicates_when_adding"))
        self.duplicatesCats.setChecked( \
            get_config("allow_duplicates_in_diff_cat"))
        
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

        current_font = self.uploadServer.font()
        
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
        
        current_font = self.uploadServer.font()
        
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
        
        self.leftAlign      .setChecked(False)
        self.keepLogs       .setChecked(True)
        self.uploadLogs     .setChecked(True)
        self.checkDuplicates.setChecked(True)
        self.duplicatesCats .setChecked(True)
        
        self.uploadServer.setText("mnemosyne-proj.dyndns.org:80")
        
    ##########################################################################
    #
    # apply
    #
    ##########################################################################

    def apply(self):

        set_config("left_align",    self.leftAlign .isOn())
        set_config("keep_logs",     self.keepLogs  .isOn())
        set_config("upload_logs",   self.uploadLogs.isOn())
        set_config("upload_server", unicode(self.uploadServer.text()))
        set_config("check_duplicates_when_adding",self.checkDuplicates.isOn())
        set_config("allow_duplicates_in_diff_cat",self.duplicatesCats.isOn())

        update_logging_status()             
        
        self.close()
        
