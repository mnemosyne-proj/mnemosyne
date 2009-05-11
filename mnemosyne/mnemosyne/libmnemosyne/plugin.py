#
# plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import _
from mnemosyne.libmnemosyne.component_manager import config
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import main_widget

class Plugin(Component):

    """A Plugin is a group of components which can be activated and
    deactivated by the user when the program is running.

    Plugins are used as a separate class, and not as mixins, in order to
    allow for the fact that a Plugin can group multiple components.

    'components' is a list of component classes (not instances) that will
    be instantiated when the Plugin becomes active.
    
    """

    name = ""
    description = ""
    activation_message = ""
    component_type = "plugin"
    components = None
    show_in_first_run_wizard = False
        
    def __init__(self):
        assert self.name and self.description and self.components, \
            "A plugin needs a name, description and components."
        self.instantiated_components = []
        
    def activate(self):
        if self.activation_message:
            main_widget().information_box(self.activation_message)
        for component in self.components:
            component = component()
            component_manager.register(component)
            component.activate()           
            self.instantiated_components.append(component)
        # Uses classes instead of instances here in order to survive pickling.  
        config()["active_plugins"].add(self.__class__)

    def deactivate(self):
        if not self.instantiated_components:
            return True
        for component in self.instantiated_components:
            if component.component_type == "card_type" and \
                   database().is_loaded():
                for card_type in database().card_types_in_use():
                    if issubclass(card_type.__class__, component.__class__):
                        main_widget().information_box(\
        _("Cannot deactivate, this card type or a clone of it is in use."))
                        return False
            component_manager.unregister(component) # Also deactivates them.
        # Uses classes instead of instances here in order to survive pickling.           
        config()["active_plugins"].remove(self.__class__)
        self.instantiated_components = []
        return True
