#
# configuration_wdgt_main.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
     ConfigurationWidget
from mnemosyne.pyqt_ui.ui_configuration_wdgt_main import \
     Ui_ConfigurationWdgtMain


class ConfigurationWdgtMain(QtGui.QWidget, Ui_ConfigurationWdgtMain,
    ConfigurationWidget):

    name = "General"

    def __init__(self, component_manager, parent):
        ConfigurationWidget.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
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
        if self.config()["memorise_sister_cards_on_same_day"] == True:
            self.memorise_sister_cards_on_same_day.setCheckState(\
                QtCore.Qt.Checked)
        else:
            self.memorise_sister_cards_on_same_day.setCheckState(\
                QtCore.Qt.Unchecked)
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
        if self.config()["show_daily_tips"] == True:
            self.tipday.setCheckState(QtCore.Qt.Unchecked)
        else:
            self.tipday.setCheckState(QtCore.Qt.Unchecked)
            
    def reset_to_defaults(self):
        self.new_cards.setCurrentIndex(0)
        self.scheduled_cards.setCurrentIndex(0)
        self.non_memorised_cards.setValue(10)
        self.memorise_sister_cards_on_same_day.setCheckState(\
                QtCore.Qt.Unchecked)
        self.media_autoplay.setCheckState(QtCore.Qt.Checked)
        self.media_controls.setCheckState(QtCore.Qt.Unchecked)
        self.upload_science_logs.setCheckState(QtCore.Qt.Checked)
        self.tipday.setCheckState(QtCore.Qt.Checked)
        
    def apply(self):
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
        if self.memorise_sister_cards_on_same_day.checkState() == \
           QtCore.Qt.Checked:
            self.config()["memorise_sister_cards_on_same_day"] = True
        else:
            self.config()["memorise_sister_cards_on_same_day"] = False
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
        if self.tipday.checkState() == QtCore.Qt.Checked:
            self.config()["show_daily_tips"] = True
