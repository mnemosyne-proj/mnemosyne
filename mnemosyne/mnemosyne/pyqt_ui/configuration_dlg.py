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
        self.vbox_layout = QtGui.QVBoxLayout(self)
        if len(self.configuration_widgets()) == 1:
            widget = self.configuration_widgets()[0](self.component_manager)
            self.vbox_layout.addWidget(widget)
        else:  
            self.tab_widget = QtGui.QTabWidget(self.main_widget())
            for widget in self.configuration_widgets():
                widget = widget(self.component_manager)
                self.tab_widget.addTab(widget, widget.name)
            widget_index = self.config()["last_configuration_wdgt"]
            if widget_index >= self.tab_widget.count():
                widget_index = 0
            self.tab_widget.setCurrentIndex(widget_index)
            self.display_widget(widget_index)
        self.vbox_layout.addWidget(self.tab_widget)       
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.addItem(QtGui.QSpacerItem(20, 20,
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.ok_button = QtGui.QPushButton(_("&OK"), self)
        self.button_layout.addWidget(self.ok_button)
        self.defaults_button = QtGui.QPushButton(_("&Defaults"), self)
        self.button_layout.addWidget(self.defaults_button)
        self.cancel_button = QtGui.QPushButton(_("&Cancel"), self)
        self.button_layout.addWidget(self.cancel_button)        
        self.vbox_layout.addLayout(self.button_layout)
        self.connect(self.ok_button, QtCore.SIGNAL("clicked()"),
                     self.accept)
        self.connect(self.defaults_button, QtCore.SIGNAL("clicked()"),
                     self.defaults)        
        self.connect(self.cancel_button,
                     QtCore.SIGNAL("clicked()"), self.reject)
        self.connect(self.tab_widget, QtCore.SIGNAL("currentChanged(int)"),
                     self.display_widget)

    def activate(self):
        self.exec_()

    def closeEvent(self, event):
        self.config()["configuration_dlg_size"] = (self.width(), self.height())
        
    def accept(self):
        self.config()["configuration_dlg_size"] = (self.width(), self.height())
        return QtGui.QDialog.accept(self)

    def defaults(self):
        print 'defaults'
        
    def display_widget(self, widget_index):
        widget = self.tab_widget.widget(widget_index)
        self.config()["last_configuration_wdgt"] = widget_index
        width, height = self.config()["configuration_dlg_size"]
        if width:
            self.resize(width, height)
