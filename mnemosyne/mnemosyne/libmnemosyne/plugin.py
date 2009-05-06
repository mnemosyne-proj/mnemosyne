#
# plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import config
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
_ = component_manager.translator


class Plugin(Component):

    """A Plugin is a group of components which can be activated and
    deactivated by the user when the program is running.

    Plugins are used as a separate class, and not as mixins, in order to
    allow for the fact that a Plugin can group multiple components.
    
    """

    name = ""
    description = ""
    activation_message = ""
    component_type = "plugin"
    show_in_first_run_wizard = False
        
    def __init__(self, components):
        assert self.name and self.description, \
            "A plugin needs a name and description."
        self.components = components
        
    def activate(self):
        if self.activation_message and ui_controller_main().widget:
            ui_controller_main().widget.information_box(\
                self.activation_message)
        for component in self.components:
            component_manager.register(component)
            # TODO: move to base class?
            if component.component_type == "scheduler":
                component.reset()
        config()["active_plugins"].add(self.__class__)

    def deactivate(self):
        for component in self.components:
            # TODO: move to manager?
            if component.component_type == "card_type" and database().is_loaded():
                for card_type in database().card_types_in_use():
                    if issubclass(card_type.__class__, component.__class__):
                        ui_controller_main().widget.information_box(\
        _("Cannot deactivate, this card type or a clone of it is in use."))
                        return False
            component_manager.unregister(component)
            # TODO: move to base class.
            from mnemosyne.libmnemosyne.component_manager import scheduler
            if component.component_type == "scheduler":
                scheduler().reset()            
        config()["active_plugins"].remove(self.__class__)
        return True
