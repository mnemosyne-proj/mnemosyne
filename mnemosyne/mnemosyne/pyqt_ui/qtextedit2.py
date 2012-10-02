#
# qtextedit2.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _


class QTextEdit2(QtGui.QTextEdit):

    """QTextEdit with extra options in popup menu."""

    def __init__(self, parent, pronunciation_hiding=None):

        """'pronunciation_hiding' is set to None when there is no
        pronunciation key to hide, and to True or False when there is one to
        hide.

        """

        QtGui.QTextEdit.__init__(self, parent)
        self.pronunciation_hiding = pronunciation_hiding
        self.setAcceptRichText(False)

    def contextMenuEvent(self, e):
        popup = self.createStandardContextMenu()
        popup.addSeparator()
        popup.addAction(_("Insert &image"), self.insert_img,
                        QtGui.QKeySequence(_("Ctrl+I")))
        popup.addAction(_("Insert &sound"), self.insert_sound,
                        QtGui.QKeySequence(_("Ctrl+S")))
        popup.addAction(_("Insert vi&deo"), self.insert_video,
                        QtGui.QKeySequence(_("Ctrl+D")))
        if self.pronunciation_hiding in [True, False]:
            popup.addSeparator()
            self.hide_action = QtGui.QAction(\
                _("&Hide pronunciation field for this card type"), popup)
            self.hide_action.setCheckable(True)
            self.hide_action.setChecked(self.pronunciation_hiding)
            self.hide_action.toggled.connect(\
                self.parent().pronunciation_hiding_toggled)
            popup.addAction(self.hide_action)
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
        filter = "(*.png *.gif *.jpg *.bmp *.jpeg *.svg *.tiff" + \
                 " *.PNG *.GIF *.jpg *.BMP *.JPEG *.SVG *.TIFF)"
        filename = self.parent().controller().show_insert_img_dialog(filter)
        if filename:
            self.insertPlainText("<img src=\"" + filename + "\">")

    def insert_sound(self):
        filter = "(*.wav *.mp3 *.ogg *.WAV *.MP3 *.OGG)"
        filename = self.parent().controller().show_insert_sound_dialog(filter)
        if filename:
            self.insertPlainText("<audio src=\"" + filename + "\">")

    def insert_video(self):
        filter = "(*.mov *.ogg *.ogv *.mp4 *.qt" + \
                 " *.MOV *.OGG *.OGV *.MP4 *.QT)"
        filename = self.parent().controller().show_insert_video_dialog(filter)
        if filename:
            self.insertPlainText("<video src=\"" + filename + "\">")



