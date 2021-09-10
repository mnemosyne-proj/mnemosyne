#
# qtextedit2.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _


class QTextEdit2(QtWidgets.QTextEdit):

    """QTextEdit with extra options in popup menu."""

    def __init__(self, parent, card_type, pronunciation_hiding):

        """'pronunciation_hiding' is set to None when there is no
        pronunciation key to hide, and to True or False when there is one to
        hide.

        """

        super().__init__(parent)
        self.pronunciation_hiding = pronunciation_hiding
        self.card_type = card_type
        # Make list of translators and pronouncers for this card type.
        language_id = self.card_type.config().card_type_property(\
            "language_id", self.card_type, default=None)
        self.translators = [] if not language_id else \
            self.card_type.component_manager.all("translator", language_id)
        self.pronouncers = [] if not language_id else \
            self.card_type.component_manager.all("pronouncer", language_id)

    def contextMenuEvent(self, e):
        popup = self.createStandardContextMenu()
        popup.addSeparator()
        popup.addAction(_("Insert &image"), self.insert_img,
                        QtGui.QKeySequence(_("Ctrl+I")))
        popup.addAction(_("Insert &sound"), self.insert_sound,
                        QtGui.QKeySequence(_("Ctrl+S")))
        popup.addAction(_("Insert vi&deo"), self.insert_video,
                        QtGui.QKeySequence(_("Ctrl+D")))
        popup.addAction(_("Insert &Flash"), self.insert_flash,
                        QtGui.QKeySequence(_("Ctrl+F")))
        # Pronunciation hiding.
        if self.pronunciation_hiding in [True, False]:
            popup.addSeparator()
            self.hide_action = QtWidgets.QAction(\
                _("&Hide pronunciation field for this card type"), popup)
            self.hide_action.setCheckable(True)
            self.hide_action.setChecked(self.pronunciation_hiding)
            self.hide_action.toggled.connect(\
                self.parent().pronunciation_hiding_toggled)
            popup.addAction(self.hide_action)
        # Translators.
        if len(self.translators):
            popup.addSeparator()
            for translator in self.translators:
                translator_action = QtWidgets.QAction(\
                    translator.popup_menu_text, popup)
                translator_action.triggered.connect(\
                    lambda checked, t=translator: self.translate(t))
                translator_action.setShortcuts([QtGui.QKeySequence("Ctrl+T")])
                popup.addAction(translator_action)
        # Pronouncers.
        if len(self.pronouncers):
            popup.addSeparator()
            for pronouncer in self.pronouncers:
                pronouncer_action = QtWidgets.QAction(\
                    pronouncer.popup_menu_text, popup)
                pronouncer_action.triggered.connect(\
                    lambda checked, p=pronouncer: self.pronounce(p))
                pronouncer_action.setShortcuts([QtGui.QKeySequence("Ctrl+P")])
                popup.addAction(pronouncer_action)
        # Show popup.
        popup.exec_(e.globalPos())

    def translate(self, translator):
        foreign_text = self.parent().foreign_text()
        translated_text = translator.show_dialog(self.card_type, foreign_text)
        if translated_text:
            self.insertPlainText(translated_text)

    def pronounce(self, pronouncer):
        foreign_text = self.parent().foreign_text()
        pronounced_text = pronouncer.show_dialog(self.card_type, foreign_text)
        if pronounced_text:
            self.insertPlainText(pronounced_text)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_I and event.modifiers() == \
            QtCore.Qt.ControlModifier:
            self.insert_img()
        elif event.key() == QtCore.Qt.Key_S and event.modifiers() == \
            QtCore.Qt.ControlModifier:
            self.insert_sound()
        elif event.key() == QtCore.Qt.Key_D and event.modifiers() == \
            QtCore.Qt.ControlModifier:
            self.insert_video()
        elif event.key() == QtCore.Qt.Key_F and event.modifiers() == \
            QtCore.Qt.ControlModifier:
            self.insert_flash()
        elif event.key() == QtCore.Qt.Key_T and event.modifiers() == \
            QtCore.Qt.ControlModifier and self.translators:
            self.translate(self.translators[-1])
        elif event.key() == QtCore.Qt.Key_P and event.modifiers() == \
            QtCore.Qt.ControlModifier and self.pronouncers:
            self.translate(self.pronouncers[-1])
        else:
            QtWidgets.QTextEdit.keyPressEvent(self, event)

    def insert_img(self):
        filter = "(*.png *.gif *.jpg *.bmp *.jpeg *.svg *.tiff *.webp" + \
                 " *.PNG *.GIF *.JPG *.BMP *.JPEG *.SVG *.TIFF *.WEBP)"
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

    def insert_flash(self):
        filter = "(*.swf *.SWF)"
        filename = self.parent().controller().show_insert_flash_dialog(filter)
        if filename:
            self.insertPlainText(\
                "<object type=\"application/x-shockwave-flash\" data=\"" \
                + filename + "\" />")
