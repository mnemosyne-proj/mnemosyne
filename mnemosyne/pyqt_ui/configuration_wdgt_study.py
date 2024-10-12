#
# configuration_wdgt_study.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
     ConfigurationWidget
from mnemosyne.pyqt_ui.ui_configuration_wdgt_study import \
     Ui_ConfigurationWdgtStudy
from mnemosyne.libmnemosyne.schedulers.cramming import RANDOM, \
    EARLIEST_FIRST, LATEST_FIRST, MOST_LAPSES_FIRST


class ConfigurationWdgtStudy(QtWidgets.QWidget, ConfigurationWidget,
    Ui_ConfigurationWdgtStudy):

    name = _("Study")

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        if self.config()["randomise_scheduled_cards"] == True:
            self.scheduled_cards.setCurrentIndex(1)
        else:
            self.scheduled_cards.setCurrentIndex(0)
        self.non_memorised_cards.setValue(self.config()\
            ["non_memorised_cards_in_hand"])
        if self.config()["randomise_new_cards"] == True:
            self.new_cards.setCurrentIndex(1)
        else:
            self.new_cards.setCurrentIndex(0)
        if self.config()["cramming_order"] == RANDOM:
            self.order.setCurrentIndex(0)
        elif self.config()["cramming_order"] == EARLIEST_FIRST:
            self.order.setCurrentIndex(1)
        elif self.config()["cramming_order"] == LATEST_FIRST:
            self.order.setCurrentIndex(2)
        elif self.config()["cramming_order"] == MOST_LAPSES_FIRST:
            self.order.setCurrentIndex(3)
        self.max_ret_reps_for_recent_cards.setValue(self.config()\
            ["max_ret_reps_for_recent_cards"])
        self.max_ret_reps_since_lapse.setValue(self.config()\
            ["max_ret_reps_since_lapse"])
        if self.config()["cramming_store_state"] == True:
            self.store_state.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self.store_state.setCheckState(QtCore.Qt.CheckState.Unchecked)

    def reset_to_defaults(self):
        answer = self.main_widget().show_question(\
            _("Reset current tab to defaults?"), _("&Yes"), _("&No"), "")
        if answer == 1:
            return
        self.scheduled_cards.setCurrentIndex(0)
        self.non_memorised_cards.setValue(10)
        self.new_cards.setCurrentIndex(0)
        self.order.setCurrentIndex(0)
        self.max_ret_reps_for_recent_cards.setValue(1)
        self.max_ret_reps_since_lapse.setValue(999999)
        self.store_state.setCheckState(QtCore.Qt.CheckState.Checked)

    def apply(self):
        if self.scheduled_cards.currentIndex() == 1:
            self.config()["randomise_scheduled_cards"] = True
        else:
            self.config()["randomise_scheduled_cards"] = False
        self.config()["non_memorised_cards_in_hand"] = \
            self.non_memorised_cards.value()
        if self.new_cards.currentIndex() == 1:
            self.config()["randomise_new_cards"] = True
        else:
            self.config()["randomise_new_cards"] = False
        if self.order.currentIndex() == 0:
            self.config()["cramming_order"] = RANDOM
        elif self.order.currentIndex() == 1:
            self.config()["cramming_order"] = EARLIEST_FIRST
        elif self.order.currentIndex() == 2:
            self.config()["cramming_order"] = LATEST_FIRST
        elif self.order.currentIndex() == 3:
            self.config()["cramming_order"] = MOST_LAPSES_FIRST
        self.config()["max_ret_reps_for_recent_cards"] = \
            self.max_ret_reps_for_recent_cards.value()
        self.config()["max_ret_reps_since_lapse"] = \
            self.max_ret_reps_since_lapse.value()
        if self.store_state.checkState() == QtCore.Qt.CheckState.Checked:
            self.config()["cramming_store_state"] = True
        else:
            self.config()["cramming_store_state"] = False


