#
# plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component_manager import component_manager


class Plugin(object):

    """A plugin is a component which can be activated and deactivated by the
    user when the program is running.  Typically, plugins derive from both 
    Plugin and the component they implement, and set the 'provides' class 
    variable to the string describing the component type.
    
    """

    name = ""
    description = ""
    active = False
    provides = ""
        
    def __init__(self):
        assert self.name and self.description, \
            "A Plugin needs a name and description."
            
    def activate(self):
        component_manager.register(self.provides, self)
        self.active = True

    def deactivate(self):        
        component_manager.unregister(self.provides, self)
        self.active = False

