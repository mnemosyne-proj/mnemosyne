#
# pronouncer_dlg.py <Peter.Bienstman@gmail.com>
#

import os
import shutil

from PyQt6 import QtGui, QtCore, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import traceback_string
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.ui_components.dialogs import PronouncerDialog
from mnemosyne.pyqt_ui.ui_pronouncer_dlg import Ui_PronouncerDlg


class DownloadThread(QtCore.QThread):

    finished_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)

    def __init__(self, pronouncer, card_type, foreign_text):
        super().__init__()
        self.pronouncer = pronouncer
        self.card_type = card_type
        self.foreign_text = foreign_text

    def run(self):
        try:
            filename = self.pronouncer.download_tmp_audio_file(\
                self.card_type, self.foreign_text)
            self.finished_signal.emit(filename)
        except Exception as e:
            self.error_signal.emit(str(e) + "\n" + traceback_string())


class PronouncerDlg(QtWidgets.QDialog, PronouncerDialog, Ui_PronouncerDlg):

    def __init__(self, pronouncer, **kwds):
        self.pronouncer = pronouncer
        super().__init__(**kwds)
        self.setupUi(self)
        self.last_foreign_text = ""
        self.tmp_filename = ""
        self.text_to_insert = ""

    def activate(self, card_type, foreign_text):
        PronouncerDialog.activate(self)
        # Set text and font for the foreign text.
        self.card_type = card_type
        fact_key = self.config().card_type_property(\
            "foreign_fact_key", card_type, default="")
        font_string = self.config().card_type_property(\
            "font", card_type, fact_key)
        if font_string:
            font = QtGui.QFont()
            font.fromString(font_string)
            self.foreign_text.setCurrentFont(font)
        self.foreign_text.setPlainText(foreign_text)
        # Set sublanguages.
        language = self.language_with_id(self.config().card_type_property(\
            "language_id", card_type))
        if len(language.sublanguages) == 0:
            self.sublanguages.hide()
            self.sublanguages_label.hide()
        else:
            previous_sublanguage_id = self.config().card_type_property(\
                "sublanguage_id", card_type)
            items = language.sublanguages.items()
            if not previous_sublanguage_id:
                items = [(None, _("<default>"))] + list(items)
            self.sublanguage_id_with_name = {}
            saved_index = 0
            for sublanguage_id, sublanguage_name in items:
                self.sublanguage_id_with_name[sublanguage_name] = sublanguage_id
                self.sublanguages.addItem(sublanguage_name)
                if previous_sublanguage_id:
                    if sublanguage_id == previous_sublanguage_id:
                        saved_index = self.sublanguages.count()-1
            if saved_index:
                self.sublanguages.setCurrentIndex(saved_index)
            # Only now it's safe to connect to the slot.
            self.sublanguages.currentTextChanged.connect(\
                self.sublanguage_changed)
        # Auto download.
        self.set_default_filename()
        self.insert_button.setEnabled(False)
        self.download_audio_and_play()
        self.exec()

    def set_default_filename(self):
        foreign_text = self.foreign_text.toPlainText()
        filename = self.pronouncer.default_filename(\
            self.card_type, foreign_text)
        self.filename_box.setText(filename)

    def foreign_text_changed(self):
        # Force the user to preview.
        self.insert_button.setEnabled(False)
        self.preview_button.setDefault(True)

    def sublanguage_changed(self):
        sublanguage_id = self.sublanguage_id_with_name[\
            self.sublanguages.currentText()]
        self.config().set_card_type_property("sublanguage_id",
            sublanguage_id, self.card_type)
        self.download_audio_and_play()

    def download_audio_and_play(self):
        self.last_foreign_text = self.foreign_text.toPlainText()
        if not self.last_foreign_text:
            return
        # Note that we need to save the QtThread as a class variable,
        # otherwise it will get garbage collected.
        self.download_thread = DownloadThread(\
            self.pronouncer, self.card_type, self.last_foreign_text)
        self.download_thread.finished_signal.connect(self.play_audio)
        self.download_thread.error_signal.connect(self.main_widget().show_error)
        self.main_widget().set_progress_text(_("Downloading..."))
        self.download_thread.start()

    def play_audio(self, filename):
        self.main_widget().close_progress()
        self.review_widget().play_media(filename)
        self.tmp_filename = filename
        self.insert_button.setEnabled(True)
        self.insert_button.setDefault(True)
        self.insert_button.setFocus()

    def preview(self):
        if self.foreign_text.toPlainText() == self.last_foreign_text:
            self.play_audio(self.tmp_filename)
        else:
            self.download_audio_and_play()

    def browse(self):
        filename = self.main_widget().get_filename_to_save(\
            self.database().media_dir(),
            _("Mp3 files (*.mp3)")).replace("\\", "/")
        if os.path.isabs(filename) and not filename.startswith(\
            self.database().media_dir().replace("\\", "/")):
            self.main_widget().show_error(\
                _("Please select a filename inside the media directory."))
            self.set_default_filename()
        else:
            if filename:
                self.filename_box.setText(filename)

    def accept(self):
        filename = self.filename_box.text().replace("\\", "/")
        if not filename:
            return QtWidgets.QDialog.accept(self)
        if os.path.isabs(filename):
            if not filename.startswith(\
                self.database().media_dir().replace("\\", "/")):
                self.main_widget().show_error(\
                    _("Please select a filename inside the media directory."))
                self.set_default_filename()
                return
            else:
                filename = contract_path(filename, self.database().media_dir())
        # By now, filename is relative to the media dir.
        # Save subdirectory for this card type.
        local_dir = os.path.dirname(filename)
        if local_dir:
            self.config()["tts_dir_for_card_type_id"]\
                [self.card_type.id] = local_dir
        full_local_dir = expand_path(local_dir, self.database().media_dir())
        if not os.path.exists(full_local_dir):
            os.makedirs(full_local_dir)
        shutil.copyfile(self.tmp_filename,
            os.path.join(self.database().media_dir(), filename))
        self.text_to_insert = "<audio src=\"" + filename + "\">"
        QtWidgets.QDialog.accept(self)
