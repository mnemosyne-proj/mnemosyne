#
# component.py <Peter.Bienstman@UGent.be>
#

class Component(object):

    """Base class of components that are registered with the component
    manager. This is a list of component types: config, log, database,
    scheduler, stopwatch, translator, filter, card_type, card_type_converter,
    card_type_widget, ui_component, renderer, ui_controller_main, main_widget,
    ui_controller_review, review_widget, plugin, hook.       

    'used_for' can store certain relationships between components, e.g.
    a card type widget is used for a certain card type.

    For efficiency reasons, not all components are instantiated immediately,
    e.g. instantiating a complex widget can take a lot of time on a mobile
    device. Some components like review widgets need to be instantiated when
    the plugin in which they are contained becomes active. Others, like card
    type widgets, are instantiated even later, e.g. when the add or edit
    dialog is shown.

    Each component has access to all of the context of the other components
    because it hold a reference to the user's component manager.

    We need to pass the context of the component manager already in the
    constructor, as many component make use of it in their __init__ method.
    This means that derived components should always call the
    Component.__init__ if they provide their own constructor.
    
    """
    
    component_type = ""
    used_for = None

    IMMEDIATELY = 0
    WHEN_PLUGIN_ACTIVE = 1
    LATER = 2
    
    instantiate = IMMEDIATELY
    
    def __init__(self, component_manager):
        self.component_manager = component_manager

    def activate(self):

        """Initialisation code called when the component is about to do actual
        work, and which can't happen in the constructor, e.g. because
        components on which it relies have not yet been registered.

        """

        pass

    def deactivate(self):        
        pass

    # Convenience functions, for easier access to all of the context of
    # libmnemosyne from within a component.
    
    def _(self):
        return self.component_manager.get_current("translator")
    
    def config(self):
        return self.component_manager.get_current("config")

    def log(self):
        return self.component_manager.get_current("log")

    def database(self):
        return self.component_manager.get_current("database")

    def scheduler(self):
        return self.component_manager.get_current("scheduler")
    
    def stopwatch(self):
        return self.component_manager.get_current("stopwatch")
    
    def main_widget(self):
        return self.component_manager.get_current("main_widget")

    def review_widget(self):
        return self.component_manager.get_current("review_widget")

    def ui_controller_main(self):
        return self.component_manager.get_current("ui_controller_main")

    def ui_controller_review(self):
        return self.component_manager.get_current("ui_controller_review")

    def card_types(self):
        return self.component_manager.get_all("card_type")

    def filters(self):
        return self.component_manager.get_all("filter")

    def plugins(self):
        return self.component_manager.get_all("plugin")

    def card_type_by_id(self, id): 
        return self.component_manager.card_type_by_id[id]
