#
# plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import _
from mnemosyne.libmnemosyne.component_manager import config
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import main_widget

class Plugin(Component):

    """A Plugin is a group of components which can be activated and
    deactivated by the user when the program is running.

    Plugins are used as a separate class, and not as mixins, in order to
    allow for the fact that a Plugin can group multiple components.

    'components' is a list of component classes (not instances) that will
    be instantiated when the Plugin becomes active.

    Activating and deactivating certain components needs to give rise to
    certain side effects. It's cumbersone to implement those in the
    'activate' and 'deactivate' methods of the components, as these also
    are called when the program is still starting up and the context can
    be completely different.
    
    """

    name = ""
    description = ""
    activation_message = ""
    component_type = "plugin"
    components = None
    show_in_first_run_wizard = False
        
    def __init__(self):
        assert self.name and self.description, \
            "A plugin needs a name and a description."
        self.instantiated_components = []
        
    def activate(self):
        if self.activation_message:
            main_widget().information_box(self.activation_message)
        # Identify components which are 'used_for' the component in this
        # plugin or this plugin itself (typically UI widgets).
        to_be_used_for = [self.__class__]
        if self.components:
            to_be_used_for += self.components
        to_register = []
        for component in to_be_used_for:
            if component in component_manager.components: # as 'used_for' key.
                for comp_type in component_manager.components[component]:
                    to_register += \
                            component_manager.components[component][comp_type]
        # Add plugin's own components.
        if self.components:        
            to_register += self.components
        # Register all these components. If they were originally 'used_for'
        # the plugin, now make them 'used_for' their true purpose.
        for component in to_register:
            if component.instantiate != Component.LATER:
                # After this call, both the class component and the instance
                # component will be registered (with the instance having
                # precendence), and the instance component will be unregistered
                # again when the plugin is deactivated
                component = component()
                if hasattr(component, "then_used_for"):
                    component.used_for = component.then_used_for
                component_manager.register(component)
                component.activate()           
                self.instantiated_components.append(component)
            else:
                component_manager.register(component)                
        # Make necessary side effects happen.
        for component in self.instantiated_components:
            if component.component_type == "scheduler" \
                   and database().is_loaded():
                from mnemosyne.libmnemosyne.component_manager \
                     import ui_controller_review
                ui_controller_review().reset()
                ui_controller_review().new_question()
        # Uses classes instead of instances here in order to survive pickling.  
        config()["active_plugins"].add(self.__class__.__name__)

    def deactivate(self):
        for component in self.instantiated_components:
            if component.component_type == "card_type" \
                   and database().is_loaded():
                for card_type in database().card_types_in_use():
                    if issubclass(card_type.__class__, component.__class__):
                        main_widget().information_box(\
        _("Cannot deactivate, this card type or a clone of it is in use."))
                        return False
            component.deactivate()
            component_manager.unregister(component)
        # Make necessary side effects happen.
        for component in self.instantiated_components:
            if component.component_type == "review_widget":
                # Some toolkits (e.g. Qt) destroy the old review widget after
                # it has been replaced by a new one, so we need to recreate
                # the old one.
                from mnemosyne.libmnemosyne.component_manager \
                     import review_widget             
                old_widget = review_widget()
                new_widget = old_widget.__class__()
                component_manager.unregister(old_widget)
                component_manager.register(new_widget)
            if component.component_type == "scheduler" and \
                   database().is_loaded():
                from mnemosyne.libmnemosyne.component_manager \
                     import ui_controller_review
                ui_controller_review().reset()
                ui_controller_review().new_question()
        # Uses names instead of instances here in order to survive pickling.
        if self.__class__.__name__ in config()["active_plugins"]:
            config()["active_plugins"].remove(self.__class__.__name__)
        self.instantiated_components = []
        return True
