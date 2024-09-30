#
# configuration_wdgt_main.py <Peter.Bienstman@gmail.com>
#

import sys

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _, \
    iso6931_code_for_language_name, language_name_for_iso6931_code
from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
    ConfigurationWidget
from mnemosyne.pyqt_ui.ui_configuration_wdgt_main import \
    Ui_ConfigurationWdgtMain


class ConfigurationWdgtMain(QtWidgets.QWidget, ConfigurationWidget,
                            Ui_ConfigurationWdgtMain):

    name = _("General")

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.save_after_n_reps.setValue(self.config()["save_after_n_reps"])
        self.max_backups.setValue(self.config()["max_backups"])
        if self.config()["upload_science_logs"] == True:
            self.upload_science_logs.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.upload_science_logs.setCheckState(QtCore.Qt.CheckState.Unchecked)
        if self.config()["QA_split"] == "fixed":
            self.card_presentation.setCurrentIndex(0)
        elif self.config()["QA_split"] == "adaptive":
            self.card_presentation.setCurrentIndex(1)
        elif self.config()["QA_split"] == "single_window":
            self.card_presentation.setCurrentIndex(2)
        language_names = ["English"]
        for language in self.gui_translator().supported_languages():
            language_names.append(language_name_for_iso6931_code[language])
        language_names.sort()
        for language_name in language_names:
            self.languages.addItem(language_name)
        self.languages.setCurrentIndex(self.languages.findText(\
            language_name_for_iso6931_code[self.config()["ui_language"]]))

    def reset_to_defaults(self):
        answer = self.main_widget().show_question(\
            _("Reset current tab to defaults?"), _("&Yes"), _("&No"), "")
        if answer == 1:
            return
        self.save_after_n_reps.setValue(10)
        self.max_backups.setValue(10)
        self.card_presentation.setCurrentIndex(0)
        self.upload_science_logs.setCheckState(QtCore.Qt.CheckState.Checked)
        self.languages.setCurrentIndex(self.languages.findText("English"))

    def apply(self):
        self.config()["save_after_n_reps"] = self.save_after_n_reps.value()
        self.config()["max_backups"] = self.max_backups.value()
        if self.upload_science_logs.checkState() == QtCore.Qt.CheckState.Checked:
            self.config()["upload_science_logs"] = True
        else:
            self.config()["upload_science_logs"] = False
        if self.card_presentation.currentIndex() == 0:
            self.config()["QA_split"] = "fixed"
        elif self.card_presentation.currentIndex() == 1:
            self.config()["QA_split"] = "adaptive"
        elif self.card_presentation.currentIndex() == 2:
            self.config()["QA_split"] = "single_window"
        self.config()["ui_language"] = iso6931_code_for_language_name(\
                self.languages.currentText())
        self.gui_translator().set_language(self.config()["ui_language"])