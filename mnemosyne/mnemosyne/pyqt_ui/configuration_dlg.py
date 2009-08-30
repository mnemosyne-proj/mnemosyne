#
# configuration_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.ui_components.dialogs import ConfigurationDialog


class ConfigurationDlg(QtGui.QDialog, ConfigurationDialog):

    """A tab widget containing several configuration widgets. The number and
    names of the tab pages are determined at run time.

    """

    def __init__(self, component_manager):
        ConfigurationDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setWindowTitle(_("Configuration"))
        self.vbox_layout = QtGui.QVBoxLayout(self)
        if len(self.configuration_widgets()) == 1:
            self.widget = self.configuration_widgets()[0](self.component_manager)
            self.vbox_layout.addWidget(self.widget)
            self.widget.display()
        else:  
            self.tab_widget = QtGui.QTabWidget(self.main_widget())
            for widget in self.configuration_widgets():
                widget = widget(self.component_manager)
                self.tab_widget.addTab(widget, widget.name)
            widget_index = self.config()["last_configuration_wdgt"]
            if widget_index >= self.tab_widget.count():
                widget_index = 0
            self.tab_widget.setCurrentIndex(widget_index)
            self.change_widget(widget_index)
            self.vbox_layout.addWidget(self.tab_widget)
            self.connect(self.tab_widget, QtCore.SIGNAL("currentChanged(int)"),
                         self.change_widget)
        self.button_layout = QtGui.QHBoxLayout()
        self.ok_button = QtGui.QPushButton(_("&OK"), self)
        self.ok_button.setAutoDefault(True)
        self.ok_button.setFocus()
        self.button_layout.addWidget(self.ok_button)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
        self.button_layout.addItem(spacerItem)
        self.defaults_button = QtGui.QPushButton(_("&Defaults"), self)
        self.button_layout.addWidget(self.defaults_button)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Minimum)
        self.button_layout.addItem(spacerItem)
        self.cancel_button = QtGui.QPushButton(_("&Cancel"), self)
        self.button_layout.addWidget(self.cancel_button)        
        self.vbox_layout.addLayout(self.button_layout)
        self.connect(self.ok_button, QtCore.SIGNAL("clicked()"),
                     self.accept)
        self.connect(self.defaults_button, QtCore.SIGNAL("clicked()"),
                     self.reset_to_defaults)        
        self.connect(self.cancel_button,
                     QtCore.SIGNAL("clicked()"), self.reject)
        width, height = self.config()["configuration_dlg_size"]
        if width:
            self.resize(width, height)
            
    def activate(self):
        self.exec_()

    def closeEvent(self, event):
        self.config()["configuration_dlg_size"] = (self.width(), self.height())
        
    def accept(self):
        if hasattr(self, "widget"):
            self.widget.apply()
        else:
            for index in range(self.tab_widget.count()):
                self.tab_widget.widget(index).apply()
        self.config()["configuration_dlg_size"] = (self.width(), self.height())
        return QtGui.QDialog.accept(self)
    
    def reset_to_defaults(self):
        if hasattr(self, "widget"):
            self.widget.reset_to_defaults()
        else:
            self.tab_widget.currentWidget().reset_to_defaults()
        
    def change_widget(self, widget_index):
        self.tab_widget.widget(widget_index).display()
        self.config()["last_configuration_wdgt"] = widget_index

