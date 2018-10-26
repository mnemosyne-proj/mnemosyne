#
# google_tts_dlg.py <Peter.Bienstman@UGent.be>
#

import os
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
        # Download audio and play.
        download_thread = DownloadThread(self.pronouncer, foreign_text)
        download_thread.finished_signal.connect(self.preview)
        download_thread.start()
        self.exec_()

    def preview(self, filename): # TODO: revisit signature
        # TODO: Only redownload if changed.
        self.review_widget().play_media(filename)

    def text_changed(self):
        pass # TODO

    def browse(self):
        export_dir = self.config()["export_dir"]
        filename = self.main_widget().get_filename_to_save(export_dir,
            _(self.format().filename_filter))
        # TODO: warn when overwriting a file
        self.filename_box.setText(filename)
        if filename:
            self.config()["export_dir"] = os.path.dirname(filename)

    def accept(self):
        filename = self.filename_box.text()
        if not filename:
            return QtWidgets.QDialog.accept(self)
        # TODO: process information
        QtWidgets.QDialog.accept(self)
