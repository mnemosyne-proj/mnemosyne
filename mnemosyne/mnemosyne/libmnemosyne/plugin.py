#
# plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import component_manager


class Plugin(Component):

    """A plugin is a component which can be activated and deactivated by the
    user when the program is running. In addition to the standard
    implementation of these (de)activation routines below, a plugin
    typically (un)register one or more other components (or 'self', if one
    uses multiple inheritance).
    
    """

    def __init__(self):
        self.name = ""
        self.description = ""
        self.active = False
        component_manager.register("plugin", self)

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
