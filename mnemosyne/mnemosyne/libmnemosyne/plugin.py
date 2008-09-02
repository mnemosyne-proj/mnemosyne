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

    name = None
    description = None
    active = False

    def __init__(self):
        assert self.name and self.description, \
            "A Plugin needs a name and description"
        # not in init, explicit: component_manager.register("plugin", self)


    # XXX KW: remove: let's not rely on plugins actually calling the base class..

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

