#
# configuration_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_configuration_dlg import Ui_ConfigurationDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ConfigurationDialog


class ConfigurationDlg(QtGui.QDialog, Ui_ConfigurationDlg, ConfigurationDialog):

    """A tab widget containing several configuration widgets. The number and
    names of the tab pages are determined at run time.

    """

    def __init__(self, component_manager):
        ConfigurationDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        for widget in self.component_manager.all("configuration_widget"):
            widget = widget(self.component_manager, parent=self)
            self.tab_widget.addTab(widget, widget.name)
        self.tab_widget.tabBar().setVisible(self.tab_widget.count() > 1)     
        widget_index = self.config()["last_configuration_wdgt"]
        if widget_index >= self.tab_widget.count():
            widget_index = 0
            self.config()["last_configuration_wdgt"] = 0
        self.tab_widget.setCurrentIndex(widget_index)
        self.ok_button.setFocus()
        width, height = self.config()["configuration_dlg_size"]
        if width:
            self.resize(width, height)
            
    def activate(self):
        self.exec_()

    def closeEvent(self, event):
        self.config()["configuration_dlg_size"] = (self.width(), self.height())
        
    def accept(self):
        self.config()["last_configuration_wdgt"] = \
            self.tab_widget.currentIndex()
        for index in range(self.tab_widget.count()):
            self.tab_widget.widget(index).apply()
        self.config()["configuration_dlg_size"] = (self.width(), self.height())
        return QtGui.QDialog.accept(self)
    
    def reset_to_defaults(self):
        self.tab_widget.currentWidget().reset_to_defaults()
        

