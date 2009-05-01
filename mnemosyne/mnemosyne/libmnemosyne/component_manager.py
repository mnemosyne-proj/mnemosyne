#
# component_manager.py <Peter.Bienstman@UGent.be>
#


class ComponentManager(object):

    """Manages the different components. Each component belongs to a type
    (database, scheduler, card_type, card_type_widget, ...).

    The component manager can also store relationships between components,
    e.g. a card_type_widget is used for a certain card_type.

    For certain components, many can be active at the same time (card types,
    filters, function hooks, ...). For others, there can be only on active
    at the same time, like schedule, database ... The idea is that the last
    one registered takes preference. This means that e.g. the default
    scheduler needs to be registered first.

    Managed components:

       ======================   ===========================================
       "config"                 configuration instance
       "log"                    logger instance
       "database"               database instance
       "scheduler"              scheduler instance
       "filter"                 filter instance
       "card_type"              card_type instance
       "card_type_converter"    card_type_converter instance
                                used for (old_type class, new_type class)
       "card_type_widget"       card_type_widget class,
                                used_for card_type class
       "renderer"               renderer instance,
                                used_for card_type class
       "ui_controller_main"     ui_controller_main instance
       "ui_controller_review"   ui_controller_review instance
       "review_widget"          review_widget class
                                used_for scheduler class 
       "plugin"                 plugin instance
       "function_hook"          function hook instance
                                used_for hookpoint_name
       ======================   ===========================================
       
    Note: for widgets we store the class name as opposed to an instance,
    since creating widgets can be time consuming, and we want to create
    e.g. card type widgets only when they are really needed.

    """
        
    def __init__(self):
        self.components = {} # { used_for : {type : [component]} }
        self.card_type_by_id = {}

    def register(self, type, component, used_for=None):
        
        """For type, component and used_for, see the table above."""
       
        if not self.components.has_key(used_for):
            self.components[used_for] = {}
        if not self.components[used_for].has_key(type):
            self.components[used_for][type] = [component]
        else:
            if component not in self.components[used_for][type]:
                self.components[used_for][type].append(component)         
        if type == "card_type":
            self.card_type_by_id[component.id] = component
            
    def unregister(self, type, component, used_for=None):
        self.components[used_for][type].remove(component)

    def get_all(self, type, used_for=None):
        
        """For components for which there can be many active at once."""

        if used_for == None or isinstance(used_for, str):
            try:
                return self.components[used_for][type]
            except:
                return []

        # See if there is a component registered for the exact type.
        try:
            return self.components[used_for][type]
        except:
            # See if there is a component registered for the parent class.
            class_keys = [key for key in self.components.keys() if \
                          not isinstance(key, str) and not (key == None)]
            if isinstance(used_for, tuple):
                for key in class_keys:
                    if issubclass(used_for[0], key[0]) and \
                       issubclass(used_for[1], key[1]):
                        try:
                            return self.components[key][type]
                        except:
                            return []
                return []
            else:
                for key in class_keys:
                    if issubclass(used_for, key):
                        try:
                            return self.components[key][type]
                        except:
                            return []
                return []
        
    def get_current(self, type, used_for=None):
        
        """For components for which there can be only one active at any
        time.

        """

        all = self.get_all(type, used_for)
        if all == []:
            return None
        else:
            return all[-1]

        
# The component manager needs to be accessed by many different parts of the
# library, so we hold it in a global variable.

component_manager = ComponentManager()


# Convenience functions, for easier access from the outside world.

def config():
    return component_manager.get_current("config")
    
def log():
    return component_manager.get_current("log")
    
def database():
    return component_manager.get_current("database")

def scheduler():
    return component_manager.get_current("scheduler")

def ui_controller_main():
    return component_manager.get_current("ui_controller_main")

def ui_controller_review():
    return component_manager.get_current("ui_controller_review")

def card_types():
    return component_manager.get_all("card_type")

def card_type_by_id(id): # TODO KW: use named components for this.
    return component_manager.card_type_by_id[id]

def filters():
    return component_manager.get_all("filter")

def plugins():
    return component_manager.get_all("plugin")
