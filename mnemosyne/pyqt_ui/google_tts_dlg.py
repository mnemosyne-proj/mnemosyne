#
# google_tts_dlg.py <Peter.Bienstman@UGent.be>
#

import os
import shutil
import datetime
from PyQt5 import QtGui, QtCore, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import make_filename_unique
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.ui_components.dialogs import PronouncerDialog
from mnemosyne.pyqt_ui.ui_google_tts_dlg import Ui_GoogleTTSDlg


class DownloadThread(QtCore.QThread):

    finished_signal = QtCore.pyqtSignal(str)

    def __init__(self, pronouncer, foreign_text):
        super().__init__()
        self.pronouncer = pronouncer
        self.foreign_text = foreign_text

    def run(self):
        filename = self.pronouncer.download_tmp_audio_file(self.foreign_text)
        self.finished_signal.emit(filename)


class GoogleTTSDlg(QtWidgets.QDialog, PronouncerDialog, Ui_GoogleTTSDlg):

    used_for = "ar"  # TMP

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
        self.set_default_filename()
        self.insert_button.setEnabled(False)
        self.download_audio_and_play()
        self.exec_()

    def set_default_filename(self):
        foreign_text = self.foreign_text.toPlainText()
        if len(foreign_text) < 10:
            filename = foreign_text + ".mp3"
        else:
            filename = datetime.datetime.today().strftime("%Y%m%d.mp3")
        local_dir = self.config()["google_tts_dir_for_card_type"]\
            .get(self.card_type, "")
        filename = os.path.join(local_dir, filename)
        full_path = expand_path(filename, self.database().media_dir())
        full_path = make_filename_unique(full_path)
        filename = contract_path(full_path, self.database().media_dir())
        self.filename_box.setText(filename)

    def foreign_text_changed(self):
        # Force the user to preview.
        self.insert_button.setEnabled(False)
        self.preview_button.setDefault(True)

    def download_audio_and_play(self):
        self.last_foreign_text = self.foreign_text.toPlainText()
        download_thread = DownloadThread(\
            self.pronouncer, self.last_foreign_text)
        download_thread.finished_signal.connect(self.play_audio)
        self.main_widget().set_progress_text(_("Downloading..."))
        download_thread.start()

    def play_audio(self, filename):
        self.main_widget().close_progress()
        self.review_widget().play_media(filename)
        self.tmp_filename = filename
        self.insert_button.setEnabled(True)
        self.insert_button.setDefault(True)

    def preview(self):
        if self.foreign_text.toPlainText() == self.last_foreign_text:
            self.play_audio(self.tmp_filename)
        else:
            self.download_audio_and_play()

    def browse(self):
        filename = self.main_widget().get_filename_to_save(\
            self.database().media_dir(),
            _("Mp3 files (*.mp3)"))
        if os.path.isabs(filename) and not filename.startswith(\
            self.database().media_dir()):
            self.main_widget().show_error(\
                _("Please select a filename inside the media directory."))
            self.set_default_filename()
        else:
            if filename:
                self.filename_box.setText(filename)

    def accept(self):
        filename = self.filename_box.text()
        if not filename:
            return QtWidgets.QDialog.accept(self)
        if os.path.isabs(filename):
            if not filename.startswith(self.database().media_dir()):
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
            self.config()["google_tts_dir_for_card_type"][self.card_type] \
                = local_dir
        full_local_dir = expand_path(local_dir, self.database().media_dir())
        if not os.path.exists(full_local_dir):
            os.makedirs(full_local_dir)
        shutil.copyfile(self.tmp_filename,
            os.path.join(self.database().media_dir(), filename))
        self.text_to_insert = "<audio src=\"" + filename + "\">"
        QtWidgets.QDialog.accept(self)
