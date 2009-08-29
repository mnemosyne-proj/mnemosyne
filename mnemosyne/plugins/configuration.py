 
# configuration.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.plugin import Plugin


# Hook to set default configuration values.

class MyPluginConfiguration(Hook):

    used_for = "configuration_defaults"

    def run(self):
        self.config().setdefault("my_value", 10)
        

# The actual plugin.

class SettingsExamplePlugin(Plugin):
    
    name = "Settings example"
    description = "Example on how to store settings for your plugin"
    components = [MyPluginConfiguration]
    
    def __init__(self, component_manager):
        Plugin.__init__(self, component_manager)
        
    def activate(self):
        Plugin.activate(self)
        self.main_widget().information_box("My value is %d" % \
                                           self.config()["my_value"]) 


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(SettingsExamplePlugin)


# Widget to edit the configuration values.

from mnemosyne.libmnemosyne.ui_components.configuration_widget import \
     ConfigurationWidget

class MyConfigurationWdgt(QtGui.QWidget, ConfigurationWidget):

    def __init__(self, component_manager):
        ConfigurationWidget.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        

    def display(self):
        if self.config()["randomise_new_cards"] == True:
            self.new_cards.setCurrentIndex(1)
        else:
            self.new_cards.setCurrentIndex(0)
        if self.config()["randomise_scheduled_cards"] == True:
            self.scheduled_cards.setCurrentIndex(1)
        else:
            self.scheduled_cards.setCurrentIndex(0)
        self.grade_0_cards.setValue(self.config()["grade_0_cards_in_hand"])
        if self.config()["memorise_related_cards_on_same_day"] == True:
            self.memorise_related_cards_on_same_day.setCheckState(\
                QtCore.Qt.Checked)
        else:
            self.memorise_related_cards_on_same_day.setCheckState(\
                QtCore.Qt.Unchecked)
        if self.config()["media_autoplay"] == True:
            self.media_autoplay.setCheckState(QtCore.Qt.Checked)
        else:
            self.media_autoplay.setCheckState(QtCore.Qt.Unchecked)        
        if self.config()["media_controls"] == True:
            self.media_controls.setCheckState(QtCore.Qt.Checked)
        else:
            self.media_controls.setCheckState(QtCore.Qt.Unchecked)
        if self.config()["upload_logs"] == True:
            self.upload_logs.setCheckState(QtCore.Qt.Checked)
        else:
            self.upload_logs.setCheckState(QtCore.Qt.Unchecked)
            
    def reset_to_defaults(self):
        self.new_cards.setCurrentIndex(0)
        self.scheduled_cards.setCurrentIndex(0)
        self.grade_0_cards.setValue(10)
        self.memorise_related_cards_on_same_day.setCheckState(\
                QtCore.Qt.Unchecked)
        self.media_autoplay.setCheckState(QtCore.Qt.Checked)
        self.media_controls.setCheckState(QtCore.Qt.Unchecked)
        self.upload_logs.setCheckState(QtCore.Qt.Checked)
        
    def apply(self):
        if self.new_cards.currentIndex() == 1:
            self.config()["randomise_new_cards"] = True
        else:
            self.config()["randomise_new_cards"] = False
        if self.scheduled_cards.currentIndex() == 1:
            self.config()["randomise_scheduled_cards"] = True
        else:
            self.config()["randomise_scheduled_cards"] = False
        self.config()["grade_0_cards_in_hand"] = self.grade_0_cards.value()
