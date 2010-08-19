#
# qtextedit2.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _


class QTextEdit2(QtGui.QTextEdit):

    """QTextEdit with extra options in popup menu.""" 
    
    def contextMenuEvent(self, e):
        popup = self.createStandardContextMenu()
        popup.addSeparator()
        popup.addAction(_("Insert &image"), self.insert_img,
                        QtGui.QKeySequence(_("Ctrl+I")))
        popup.addAction(_("Insert &sound"), self.insert_sound,
                        QtGui.QKeySequence(_("Ctrl+S")))
        popup.addAction(_("Insert vi&deo"), self.insert_video,
                        QtGui.QKeySequence(_("Ctrl+D")))
        popup.exec_(e.globalPos())

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_I and event.modifiers() == \
            QtCore.Qt.ControlModifier:
            self.insert_img()
        elif event.key() == QtCore.Qt.Key_S and event.modifiers() == \
            QtCore.Qt.ControlModifier:
            self.insert_sound()
        else:
            QtGui.QTextEdit.keyPressEvent(self, event)

    def insert_img(self):
        filter = "(*.png *.gif *.jpg *.bmp *.jpeg" + \
                 " *.PNG *.GIF *.jpg *.BMP *.JPEG)"
        fname = self.parent().controller().insert_img(filter)
        if fname:
            self.insertPlainText("<img src=\"" + fname + "\">")

    def insert_sound(self):
        filter = "(*.wav *.mp3 *.ogg *.WAV *.MP3 *.OGG)"
        fname = self.parent().controller().insert_sound(filter)
        if fname:
            self.insertPlainText("<audio src=\"" + fname + "\">")
        
    def insert_video(self):
        filter = "(*.mov *.ogg *.ogv *.mp4 *.qt" + \
                 " *.MOV *.OGG *.OGV *.MP4 *.QT)"
        fname = self.parent().controller().insert_video(filter)
        if fname:
            self.insertPlainText("<video src=\"" + fname + "\">")
            
