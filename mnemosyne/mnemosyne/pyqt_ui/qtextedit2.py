##############################################################################
#
# QTextEdit with extra options in popup menu <Peter.Bienstman@UGent.be>
#
# These get merged into the frm.py files by some sed magic, so that we
# can still used qt designer easily.
#
##############################################################################

from qt import *
from mnemosyne.core import *
import os



##############################################################################
#
# QTextEdit2
#
##############################################################################

class QTextEdit2(QTextEdit):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent=None, name=None):
        
        QTextEdit.__init__(self, parent, name)



    ##########################################################################
    #
    # createPopupMenu
    #
    ##########################################################################
        
    def createPopupMenu(self, pos):

        popup = QTextEdit.createPopupMenu(self, pos)
        popup.insertSeparator()
        popup.insertItem(self.tr("Insert &picture"),
                         self.insert_img, 'Ctrl+P')
        popup.insertItem(self.tr("Insert &sound"),      
                         self.insert_sound, 'Ctrl+S')

        if self.parent().allow_3_way():
                    
            popup.insertSeparator()
            popup.insertItem(self.tr("&3-way input"),
                             self.toggle_3_way, 'Ctrl+3', 333)

            popup.setItemChecked(333, get_config("3_way_input"))
        
        return popup


    
    ##########################################################################
    #
    # keyPressEvent
    #
    ##########################################################################
    
    def keyPressEvent(self, event):
        
        if event.key() == Qt.Key_P and event.state() == Qt.ControlButton:
            self.insert_img()
        elif event.key() == Qt.Key_S and event.state() == Qt.ControlButton:
            self.insert_sound()
        elif event.key() == Qt.Key_3 and event.state() == Qt.ControlButton:
            self.toggle_3_way()
        else:
            QTextEdit.keyPressEvent(self, event)



    ##########################################################################
    #
    # insert_img
    #
    ##########################################################################
    
    def insert_img(self):

        path = get_config("import_img_dir")
        fname = unicode(QFileDialog.getOpenFileName(path,\
                                                    "*")).encode("utf-8")
        if fname:
            self.insert("<img src=\""+contract_path(fname)+"\">")
            set_config("import_img_dir", os.path.dirname(fname))


        
    ##########################################################################
    #
    # insert_sound
    #
    ##########################################################################
    
    def insert_sound(self):

        path = get_config("import_sound_dir")
        fname = unicode(QFileDialog.getOpenFileName(path,\
                                                  "*")).encode("utf-8")
        if fname:
            self.insert("<sound src=\""+contract_path(fname)+"\">")
            set_config("import_sound_dir", os.path.dirname(fname))


        
    ##########################################################################
    #
    # toggle_3_way
    #
    ##########################################################################
    
    def toggle_3_way(self):
        
        b = not get_config("3_way_input")
        set_config("3_way_input", b)

        self.emit(PYSIGNAL("3_way_input_toggled"), ())
        
