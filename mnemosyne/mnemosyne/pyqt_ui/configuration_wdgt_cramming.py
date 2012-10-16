#
# configuration_wdgt_cramming.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
     ConfigurationWidget
from mnemosyne.pyqt_ui.ui_configuration_wdgt_cramming import \
     Ui_ConfigurationWdgtCramming
from mnemosyne.libmnemosyne.schedulers.cramming import RANDOM, \
    EARLIEST_FIRST, LATEST_FIRST, MOST_LAPSES_FIRST


class ConfigurationWdgtCramming(QtGui.QWidget,
    Ui_ConfigurationWdgtCramming, ConfigurationWidget):

    name = _("Cramming")

    def __init__(self, component_manager, parent):
        ConfigurationWidget.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        if self.config()["cramming_order"] == RANDOM:
            self.order.setCurrentIndex(0)
        elif self.config()["cramming_order"] == EARLIEST_FIRST:
            self.order.setCurrentIndex(1)
        elif self.config()["cramming_order"] == LATEST_FIRST:
            self.order.setCurrentIndex(2)
        elif self.config()["cramming_order"] == MOST_LAPSES_FIRST:
            self.order.setCurrentIndex(3)
        if self.config()["cramming_store_state"] == True:
            self.store_state.setCheckState(QtCore.Qt.Checked)
        else:
            self.store_state.setCheckState(QtCore.Qt.Unchecked)

    def reset_to_defaults(self):
        answer = self.main_widget().show_question(\
            _("Reset current tab to defaults?"), _("&Yes"), _("&No"), "")
        if answer == 1:
            return
        self.order.setCurrentIndex(0)
        self.store_state.setCheckState(QtCore.Qt.Checked)

    def apply(self):
        if self.order.currentIndex() == 0:
            self.config()["cramming_order"] = RANDOM
        elif self.order.currentIndex() == 1:
            self.config()["cramming_order"] = EARLIEST_FIRST
        elif self.order.currentIndex() == 2:
            self.config()["cramming_order"] = LATEST_FIRST
        elif self.order.currentIndex() == 3:
            self.config()["cramming_order"] = MOST_LAPSES_FIRST
        if self.store_state.checkState() == QtCore.Qt.Checked:
            self.config()["cramming_store_state"] = True
        else:
            self.config()["cramming_store_state"] = False


