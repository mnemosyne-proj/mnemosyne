#
# qtextedit2.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _


class QTextEdit2(QtGui.QTextEdit):

    "QTextEdit with extra options in popup menu" 
    
    def __init__(self, parent=None):
        QtGui.QTextEdit.__init__(self, parent)

    def contextMenuEvent(self, e):
        popup = self.createStandardContextMenu()
        popup.addSeparator()
        popup.addAction(_("Insert &image"), self.insert_img,
                        QtGui.QKeySequence(_("Ctrl+I")))
        popup.addAction(_("Insert &sound"), self.insert_sound,
                        QtGui.QKeySequence(_("Ctrl+S")))
        popup.exec_(e.globalPos())

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_I and e.modifiers() == \
            QtCore.Qt.ControlModifier:
            self.insert_img()
        elif e.key() == QtCore.Qt.Key_S and e.modifiers() == \
            QtCore.Qt.ControlModifier:
            self.insert_sound()
        else:
            QtGui.QTextEdit.keyPressEvent(self, e)

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
        


        
