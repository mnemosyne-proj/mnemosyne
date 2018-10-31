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

    def activate(self, card_type, foreign_text):
        PronouncerDialog.activate(self)
        # Set text and font for the foreign text.
        fact_key = self.config().card_type_property(\
            "foreign_fact_key", card_type, default="")
        font_string = self.config().card_type_property(\
            "font", card_type, fact_key)
        if font_string:
            font = QtGui.QFont()
            font.fromString(font_string)
            self.foreign_text.setCurrentFont(font)
        self.foreign_text.setPlainText(foreign_text)
        # Default filename.
        if len(foreign_text) < 10:
            filename = foreign_text + ".mp3"
        else:
            filename = datetime.datetime.today().strftime("%Y%m%d.mp3")
        full_path = expand_path(filename, self.database().media_dir())
        full_path = make_filename_unique(full_path)
        filename = contract_path(filename, self.database().media_dir())
        self.filename_box.setText(filename)
        # Execute.
        self.download_audio_and_play()
        self.exec_()

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

    def preview(self):
        if self.foreign_text.toPlainText() == self.last_foreign_text:
            self.play_audio(self.tmp_filename)
        else:
            self.download_audio_and_play()

    def browse(self):
        filename = self.main_widget().get_filename_to_save(\
            self.database().media_dir(),
            _("Mp3 files ()*.mp3"))
        self.filename_box.setText(filename)

    def accept(self):
        # TODO: wait until file has been downloaded
        filename = self.filename_box.text()
        # TODO: make sure the filename is local to the media dir.
        if not filename:# TODO: error
            self.text_to_insert = ""
            return QtWidgets.QDialog.accept(self)
        # fix cancelling dialog.
        shutil.copyfile(self.tmp_filename,
            os.path.join(self.database().media_dir(), filename))
        self.text_to_insert = "<audio src=\"" + filename + "\">"
        QtWidgets.QDialog.accept(self)
