 
# configuration.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui

from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.plugin import Plugin


# Hook to set default configuration values.

class MyPluginConfiguration(Hook):

    used_for = "configuration_defaults"

    def run(self):
        self.config().setdefault("my_value", 10)


# Widget to edit the configuration values.

from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
     ConfigurationWidget

class MyConfigurationWdgt(QtGui.QWidget, ConfigurationWidget):

    name = "My plugin"

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.vlayout = QtGui.QVBoxLayout(self)
        self.hlayout = QtGui.QHBoxLayout()
        self.label = QtGui.QLabel("My value")
        self.hlayout.addWidget(self.label)
        self.my_value = QtGui.QSpinBox(self)
        self.my_value.setValue(self.config()["my_value"])
        self.hlayout.addWidget(self.my_value)
        self.vlayout.addLayout(self.hlayout)
            
    def reset_to_defaults(self):
        self.my_value.setValue(10)
        
    def apply(self):
        self.config()["my_value"] = self.my_value.value()


# The actual plugin.

class SettingsExamplePlugin(Plugin):
    
    name = "Settings example"
    description = "Example on how to store settings for your plugin"
    components = [MyPluginConfiguration, MyConfigurationWdgt]
    
    def __init__(self, component_manager):
        Plugin.__init__(self, component_manager)
        
    def activate(self):
        Plugin.activate(self)
        self.main_widget().show_information("My value is %d" % \
                                           self.config()["my_value"]) 


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(SettingsExamplePlugin)
