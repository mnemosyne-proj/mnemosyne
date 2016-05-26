#
# configuration_wdgt_main.py <Peter.Bienstman@UGent.be>
#

import sys

from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.translator import _, \
    iso6931_code_for_language_name, language_name_for_iso6931_code
from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
    ConfigurationWidget
from mnemosyne.pyqt_ui.ui_configuration_wdgt_main import \
    Ui_ConfigurationWdgtMain


class ConfigurationWdgtMain(QtWidgets.QWidget, Ui_ConfigurationWdgtMain,
    ConfigurationWidget):

    name = _("General")

    def __init__(self, component_manager, parent):
        super().__init__(parent, component_manager=component_manager)
        self.setupUi(self)
        if self.config()["randomise_new_cards"] == True:
            self.new_cards.setCurrentIndex(1)
        else:
            self.new_cards.setCurrentIndex(0)
        if self.config()["randomise_scheduled_cards"] == True:
            self.scheduled_cards.setCurrentIndex(1)
        else:
            self.scheduled_cards.setCurrentIndex(0)
        self.non_memorised_cards.setValue(self.config()\
            ["non_memorised_cards_in_hand"])
        self.save_after_n_reps.setValue(self.config()\
            ["save_after_n_reps"])
        if self.config()["media_autoplay"] == True:
            self.media_autoplay.setCheckState(QtCore.Qt.Checked)
        else:
            self.media_autoplay.setCheckState(QtCore.Qt.Unchecked)
        if self.config()["media_controls"] == True:
            self.media_controls.setCheckState(QtCore.Qt.Checked)
        else:
            self.media_controls.setCheckState(QtCore.Qt.Unchecked)
        if self.config()["upload_science_logs"] == True:
            self.upload_science_logs.setCheckState(QtCore.Qt.Checked)
        else:
            self.upload_science_logs.setCheckState(QtCore.Qt.Unchecked)
        language_names = ["English"]
        for language in self.translator().supported_languages():
            language_names.append(language_name_for_iso6931_code[language])
        language_names.sort()
        for language_name in language_names:
            self.languages.addItem(language_name)
        self.languages.setCurrentIndex(self.languages.findText(\
            language_name_for_iso6931_code[self.config()["ui_language"]]))
        self.media_autoplay.stateChanged.connect(self.changed_media_autoplay)
        if sys.platform == "win32":
            self.audio_box.hide()

    def changed_media_autoplay(self, state):
        if state == QtCore.Qt.Unchecked:
            self.media_controls.setCheckState(QtCore.Qt.Checked)

    def reset_to_defaults(self):
        answer = self.main_widget().show_question(\
            _("Reset current tab to defaults?"), _("&Yes"), _("&No"), "")
        if answer == 1:
            return
        self.new_cards.setCurrentIndex(0)
        self.scheduled_cards.setCurrentIndex(0)
        self.non_memorised_cards.setValue(10)
        self.save_after_n_reps.setValue(10)
        self.media_autoplay.setCheckState(QtCore.Qt.Checked)
        self.media_controls.setCheckState(QtCore.Qt.Unchecked)
        self.upload_science_logs.setCheckState(QtCore.Qt.Checked)
        self.languages.setCurrentIndex(self.languages.findText("English"))

    def apply(self):
        self.config()["ui_language"] = iso6931_code_for_language_name(\
                str(self.languages.currentText()))
        self.translator().set_language(self.config()["ui_language"])
        if self.new_cards.currentIndex() == 1:
            self.config()["randomise_new_cards"] = True
        else:
            self.config()["randomise_new_cards"] = False
        if self.scheduled_cards.currentIndex() == 1:
            self.config()["randomise_scheduled_cards"] = True
        else:
            self.config()["randomise_scheduled_cards"] = False
        self.config()["non_memorised_cards_in_hand"] = \
            self.non_memorised_cards.value()
        self.config()["save_after_n_reps"] = \
            self.save_after_n_reps.value()
        if self.media_autoplay.checkState() == QtCore.Qt.Checked:
            self.config()["media_autoplay"] = True
        else:
            self.config()["media_autoplay"] = False
        if self.media_controls.checkState() == QtCore.Qt.Checked:
            self.config()["media_controls"] = True
        else:
            self.config()["media_controls"] = False
        if self.upload_science_logs.checkState() == QtCore.Qt.Checked:
            self.config()["upload_science_logs"] = True
        else:
            self.config()["upload_science_logs"] = False
