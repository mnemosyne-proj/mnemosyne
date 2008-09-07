#
# plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import component_manager


class Plugin(Component):

    """A plugin is a component which can be activated and deactivated by the
    user when the program is running.  Typically, plugins derive from both 
    Plugin and the Component they implement, and set the 'provides' class 
    variable to the string describing the component type.
    
    """

    name = None
    description = None
    active = False
    provides = ""

    def __init__(self):
        assert Plugin.name and Plugin.description, \
            "A Plugin needs a name and description."

    def activate(self):
        component_manager.register(Plugin.provides, self)
        self.active = True

    def deactivate(self):        
        component_manager.unregister(Plugin.provides, self)
        self.active = False

