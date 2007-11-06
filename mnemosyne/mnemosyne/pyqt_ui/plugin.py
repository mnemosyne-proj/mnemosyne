##############################################################################
#
# Utilies to write plugins <Peter.Bienstman@UGent.be>
#
##############################################################################

##############################################################################
#
# get_main_widget
#
#   A bit kludgy...
#
##############################################################################

import qt

def get_main_widget():
    
    import mnemosyne.pyqt_ui.main_dlg
    
    for w in qt.qApp.topLevelWidgets():
        if type(w) == mnemosyne.pyqt_ui.main_dlg.MainDlg:
            return w
