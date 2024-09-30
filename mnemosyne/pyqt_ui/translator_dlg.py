#
# translator_dlg.py <Peter.Bienstman@gmail.com>
#

import os
import shutil

from PyQt6 import QtGui, QtCore, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.utils import traceback_string
from mnemosyne.libmnemosyne.utils import expand_path, contract_path
from mnemosyne.libmnemosyne.ui_components.dialogs import TranslatorDialog
from mnemosyne.pyqt_ui.ui_translator_dlg import Ui_TranslatorDlg



class DownloadThread(QtCore.QThread):

    finished_signal = QtCore.pyqtSignal(str)
    error_signal = QtCore.pyqtSignal(str)

    def __init__(self, translator, card_type, foreign_text, target_language_id):
        super().__init__()
        self.translator = translator
        self.card_type = card_type
        self.foreign_text = foreign_text
        self.target_language_id = target_language_id

    def run(self):
        try:
            translation = self.translator.translate(\
                self.card_type, self.foreign_text, self.target_language_id)
            if translation:
                self.finished_signal.emit(translation)
            else:
                self.error_signal.emit(_("Could not contact Google servers..."))
        except Exception as e:
            self.error_signal.emit(str(e) + "\n" + traceback_string())


class TranslatorDlg(QtWidgets.QDialog, TranslatorDialog, Ui_TranslatorDlg):

    def __init__(self, translator, **kwds):
        self.translator = translator
        super().__init__(**kwds)
        self.setupUi(self)
        self.last_foreign_text = ""
        self.text_to_insert = ""

    def activate(self, card_type, foreign_text):
        TranslatorDialog.activate(self)
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
        # Set target language.
        self.target_language_id = self.config().card_type_property(\
            "translation_language_id", card_type, default="en")
        self.language_id_with_name = {}
        for language in self.languages():
            self.language_id_with_name[language.name] = language.used_for
            self.target_languages.addItem(language.name)
            if language.used_for == self.target_language_id:
                saved_index = self.target_languages.count()-1
        self.target_languages.setCurrentIndex(saved_index)
        # Only now it's safe to connect to the slot.
        self.target_languages.currentTextChanged.connect(\
            self.target_language_changed)
        # Auto download.
        self.insert_button.setEnabled(False)
        self.download_translation()
        self.exec()

    def foreign_text_changed(self):
        # Force the user to preview.
        self.insert_button.setEnabled(False)
        self.preview_button.setDefault(True)

    def target_language_changed(self):
        self.target_language_id = self.language_id_with_name[\
            self.target_languages.currentText()]
        self.config().set_card_type_property("translation_language_id",
            self.target_language_id, self.card_type)
        self.download_translation()

    def download_translation(self):
        self.last_foreign_text = self.foreign_text.toPlainText()
        if not self.last_foreign_text:
            return
        # Note that we need to save the QtThread as a class variable,
        # otherwise it will get garbage collected.
        self.download_thread = DownloadThread(self.translator, self.card_type,
            self.last_foreign_text, self.target_language_id)
        self.download_thread.finished_signal.connect(self.show_translation)
        self.download_thread.error_signal.connect(self.show_error)
        self.main_widget().set_progress_text(_("Downloading..."))
        self.download_thread.start()

    def show_error(self, error_message):
        self.main_widget().close_progress()
        self.main_widget().show_error(error_message)
        
    def show_translation(self, translation):
        self.main_widget().close_progress()
        self.translated_text.setPlainText(translation)
        self.insert_button.setEnabled(True)
        self.insert_button.setDefault(True)
        self.insert_button.setFocus()

    def preview(self):
        if self.foreign_text.toPlainText() != self.last_foreign_text:
            self.download_translation()

    def accept(self):
        self.text_to_insert = self.translated_text.toPlainText()
        QtWidgets.QDialog.accept(self)
