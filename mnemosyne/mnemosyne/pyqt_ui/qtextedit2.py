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
        popup.insertItem(self.trUtf8("Insert &image"),
                         self.insert_img,
                         QKeySequence(self.trUtf8("Ctrl+I")))
        popup.insertItem(self.trUtf8("Insert &sound"),
                         self.insert_sound,
                         QKeySequence(self.trUtf8("Ctrl+S")))

        if self.parent().allow_3_sided():
                    
            popup.insertSeparator()
            popup.insertItem(self.trUtf8("&3-sided input"),
                             self.toggle_3_sided, Qt.Key_unknown, 333)

            popup.setItemChecked(333, get_config("3_sided_input"))
        
        return popup


    
    ##########################################################################
    #
    # keyPressEvent
    #
    ##########################################################################
    
    def keyPressEvent(self, e):
        
        if e.key() == Qt.Key_I and e.state() == Qt.ControlButton:
            self.insert_img()
        elif e.key() == Qt.Key_S and e.state() == Qt.ControlButton:
            self.insert_sound()
        elif e.key() == Qt.Key_3 and e.state() == Qt.ControlButton:
            self.toggle_3_sided()
        else:
            QTextEdit.keyPressEvent(self, e)



    ##########################################################################
    #
    # insert_img
    #
    ##########################################################################
    
    def insert_img(self):

        path = expand_path(get_config("import_img_dir"))

        fname = unicode(QFileDialog.getOpenFileName(path,
                  self.trUtf8("Image files").append(QString(\
                    " (*.png *.PNG *.gif *.GIF")).append(QString(\
                    " *.jpg *.JPG *.bmp *.BMP *.jpeg *.JPEG)")),
                  self, None, self.trUtf8("Insert image")))
        if fname:
            self.insert("<img src=\""+contract_path(fname)+"\">")
            set_config("import_img_dir", \
                       contract_path(os.path.dirname(fname)))


        
    ##########################################################################
    #
    # insert_sound
    #
    ##########################################################################
    
    def insert_sound(self):

        path = expand_path(get_config("import_sound_dir"))
        
        fname = unicode(QFileDialog.getOpenFileName(path,\
                  self.trUtf8("Sound files").append(QString(\
                    " (*.wav *.WAV *.mp3 *.MP3 *.ogg *.OGG)")),
                  self, None, self.trUtf8("Insert sound")))
        
        if fname:
            self.insert("<sound src=\""+contract_path(fname)+"\">")
            set_config("import_sound_dir", \
                       contract_path(os.path.dirname(fname)))


        
    ##########################################################################
    #
    # toggle_3_sided
    #
    ##########################################################################
    
    def toggle_3_sided(self):
        
        b = not get_config("3_sided_input")
        set_config("3_sided_input", b)

        self.emit(PYSIGNAL("3_sided_input_toggled"), ())
        
