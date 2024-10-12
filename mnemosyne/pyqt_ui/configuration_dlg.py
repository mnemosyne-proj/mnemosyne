#
# configuration_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_configuration_dlg import Ui_ConfigurationDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ConfigurationDialog


class ConfigurationDlg(QtWidgets.QDialog, ConfigurationDialog, Ui_ConfigurationDlg):

    """A tab widget containing several configuration widgets. The number and
    names of the tab pages are determined at run time.

    """

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        for widget in self.component_manager.all("configuration_widget"):
            widget = widget(component_manager=self.component_manager, parent=self)
            self.tab_widget.addTab(widget, _(widget.name))
        self.tab_widget.tabBar().setVisible(self.tab_widget.count() > 1)
        widget_index = self.config()["previous_configuration_wdgt"]
        if widget_index >= self.tab_widget.count():
            widget_index = 0
            self.config()["previous_configuration_wdgt"] = 0
        self.tab_widget.setCurrentIndex(widget_index)
        self.ok_button.setFocus()
        state = self.config()["configuration_dlg_state"]
        if state:
            self.restoreGeometry(state)

    def activate(self):
        ConfigurationDialog.activate(self)
        self.exec()

    def _store_state(self):
        self.config()["configuration_dlg_state"] = self.saveGeometry()

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()

    def accept(self):
        self.config()["previous_configuration_wdgt"] = \
            self.tab_widget.currentIndex()
        for index in range(self.tab_widget.count()):
            self.tab_widget.widget(index).apply()
        self._store_state()
        return QtWidgets.QDialog.accept(self)

    def reject(self):
        for index in range(self.tab_widget.count()):
            if hasattr(self.tab_widget.widget(index), "reject"):
                self.tab_widget.widget(index).reject()
        return QtWidgets.QDialog.reject(self)

    def reset_to_defaults(self):
        self.tab_widget.currentWidget().reset_to_defaults()


