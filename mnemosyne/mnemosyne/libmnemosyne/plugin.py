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
        self.registered_components = []
        self.review_reset_needed = False
            
    def activate(self):
        if self.instantiated_components or self.registered_components:
            return
        # See if we need to reset the review process.
        self.review_reset_needed = False
        for component in self.components:
            if component.component_type == "scheduler" or \
               component.component_type == "review_controller":
                self.review_reset_needed = True
        # Register all our components. Instantiate them if needed.
        for component in self.components:
            if component.instantiate == Component.IMMEDIATELY:
                component = component(self.component_manager)
                self.component_manager.register(component)                
                component.activate()           
                self.instantiated_components.append(component)
            else:
                self.component_manager.register(component)
                self.registered_components.append(component)
        # Make necessary side effects happen.
        for component in self.components:
            if component.used_for == "configuration_defaults":
                component(self.component_manager).run()
        db = self.database()
        if db and db.is_loaded():
            for component in self.instantiated_components:
                if component.component_type == "card_type":
                    for criterion in db.get_activity_criteria():
                        criterion.card_type_created(component)
                        db.update_activity_criterion(criterion)
        if self.database().is_loaded() and self.review_reset_needed:
            self.review_controller().reset()
            self.log().started_scheduler()
        # Use names instead of instances here in order to survive pickling.  
        self.config()["active_plugins"].add(self.__class__.__name__)
                    
    def deactivate(self):
        db = self.database()
        # Check if we are allowed to deactivate a card type.
        if db and db.is_loaded():
            for component in self.instantiated_components:
                if component.component_type == "card_type":
                    for card_type in self.database().card_types_in_use():
                        if issubclass(card_type.__class__,
                                      component.__class__):
                            self.main_widget().information_box(\
          _("Cannot deactivate, this card type or a clone of it is in use."))
                            return False
                    for criterion in db.get_activity_criteria():
                        criterion.card_type_deleted(component)
                        db.update_activity_criterion(criterion)                            
        # Deactivate and unregister components.  
        for component in self.instantiated_components:
            component.deactivate()
            self.component_manager.unregister(component)
        for component in self.registered_components:
            self.component_manager.unregister(component)
        # If we are shutting down and the database is gone, don't worry about
        # side effects.
        if not self.database():
            return True
        # Make necessary side effects happen.
        if self.review_reset_needed:
            self.review_controller().reset()
            self.log().started_scheduler()
        # Use names instead of instances here in order to survive pickling.
        if self.__class__.__name__ in self.config()["active_plugins"]:
            self.config()["active_plugins"].remove(self.__class__.__name__)
        self.instantiated_components = []
        self.registered_components = []        
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
