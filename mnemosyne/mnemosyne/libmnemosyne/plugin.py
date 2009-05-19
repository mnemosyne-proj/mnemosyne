#
# plugin.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component


class Plugin(Component):

    """A Plugin is a group of components which can be activated and
    deactivated by the user when the program is running.

    Plugins are used as a separate class, and not as mixins, in order to
    allow for the fact that a Plugin can group multiple components.

    'components' is a list of component classes (not instances) that will
    be registered and/or instantiated when the Plugin becomes active.

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
    components = []
    show_in_first_run_wizard = False
        
    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        assert self.name and self.description, \
            "A plugin needs a name and a description."
        self.instantiated_components = []
        
    def activate(self):
        # Register all our components. Instantiate them if needed.
        for component in self.components:
            if component.instantiate != Component.LATER:
                component = component(self.component_manager)
                self.component_manager.register(component)
                # Now, both the class component and the instance component
                # will be registered (with the instance having precendence),
                # and the instance component will be unregistered again when
                # the plugin is deactivated.                
                component.activate()           
                self.instantiated_components.append(component)
            else:
                self.component_manager.register(component)                
        # Make necessary side effects happen.
        for component in self.instantiated_components:
            if component.component_type == "scheduler" \
                   and self.database().is_loaded():
                self.ui_controller_review().reset()
                self.ui_controller_review().new_question()
        # Use names instead of instances here in order to survive pickling.  
        self.config()["active_plugins"].add(self.__class__.__name__)

    def deactivate(self):
        # Check if we are allowed to deactivate a card type.
        for component in self.instantiated_components:
            if component.component_type == "card_type" \
                   and self.database().is_loaded():
                for card_type in self.database().card_types_in_use():
                    if issubclass(card_type.__class__, component.__class__):
                        self.main_widget().information_box(\
        _("Cannot deactivate, this card type or a clone of it is in use."))
                        return False
            component.deactivate()
            self.component_manager.unregister(component)
        # Make necessary side effects happen. We don't put all side effects in
        # a single loop, as the order is important.
        for component in self.instantiated_components:
            if component.component_type == "review_widget":
                # Some toolkits (e.g. Qt) destroy the old review widget after
                # it has been replaced by a new one, so we need to recreate
                # the old one.           
                old_widget = self.review_widget()
                new_widget = old_widget.__class__(self.component_manager)
                self.component_manager.unregister(old_widget)
                self.component_manager.register(new_widget)
        for component in self.instantiated_components:            
            if component.component_type == "scheduler" and \
                   self.database().is_loaded():
                self.ui_controller_review().reset()
                self.ui_controller_review().new_question()
        # Use names instead of instances here in order to survive pickling.
        if self.__class__.__name__ in self.config()["active_plugins"]:
            self.config()["active_plugins"].remove(self.__class__.__name__)
        self.instantiated_components = []
        return True

def register_user_plugin(plugin_class):

    """Plugins defined in the user's plugin directory don't have an easy
    access to the current component manager, which is why this convenience
    function is provided. User defined plugins only make sense in a single
    user context (a.o. because of security reasons), so we can just take the
    first registered component manager as being the correct one.

    """
    
    from component_manager import _component_managers
    key = _component_managers.keys()[0]
    component_manager = _component_managers[key]
    plugin = plugin_class(component_manager)
    component_manager.register(plugin)
