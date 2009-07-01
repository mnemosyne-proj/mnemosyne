#
# QTextEdit with extra options in popup menu <Peter.Bienstman@UGent.be>
#

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.utils import expand_path, contract_path


class QTextEdit2(QTextEdit):
    
    def __init__(self, parent=None):
        QTextEdit.__init__(self, parent)

    def contextMenuEvent(self, e):
        popup = self.createStandardContextMenu()
        popup.addSeparator()
        popup.addAction(_("Insert &image"), self.insert_img,
                        QKeySequence(_("Ctrl+I")))
        popup.addAction(_("Insert &sound"), self.insert_sound,
                        QKeySequence(_("Ctrl+S")))
        popup.exec_(e.globalPos())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_I and e.modifiers() == Qt.ControlModifier:
            self.insert_img()
        elif e.key() == Qt.Key_S and e.modifiers() == Qt.ControlModifier:
            self.insert_sound()
        else:
            QTextEdit.keyPressEvent(self, e)

    def insert_img(self):
        filter = "(*.png *.gif *.jpg *.bmp *.jpeg" + \
                 " *.PNG *.GIF *.jpg *.BMP *.JPEG)"
        fname = self.parent().ui_controller_main().insert_img(filter)
        if fname:
            self.insertPlainText("<img src=\"" + fname + "\">")

    def insert_sound(self):
        filter = "(*.wav *.mp3 *.ogg *.WAV *.MP3 *.OGG)"
        fname = self.parent().ui_controller_main().insert_sound(filter)
        if fname:
            self.insertPlainText("<audio src=\"" + fname + "\">")
        


        
