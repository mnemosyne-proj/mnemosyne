#
# component_manager.py <Peter.Bienstman@UGent.be>
#


class ComponentManager(object):

    """Manages the different components. Apart from some UI widgets, instances
    of the different components are stored (as opposed to classes). In such a
    way, the component manager stores all the state of the user.

    For certain components, many can be active at the same time (card types,
    filters, function hooks, ...). For others, there can be only on active
    at the same time, like schedule, database ... The idea is that the last
    one registered takes preference. This means that e.g. the default
    scheduler needs to be registered first.

    """
        
    def __init__(self):
        self.components = {} # { used_for : {type : [component]} }
        self.card_type_by_id = {}

    def register(self, component, in_front=False):
        
        """For type, component and used_for, see the table above."""

        if isinstance(component, type) and \
           component.instantiate == component.IMMEDIATELY:
            component = component()
        comp_type = component.component_type
        used_for = component.used_for
        if not self.components.has_key(used_for):
            self.components[used_for] = {}
        if not self.components[used_for].has_key(comp_type):
            self.components[used_for][comp_type] = [component]
        else:
            if component not in self.components[used_for][comp_type]:
                if not in_front:
                    self.components[used_for][comp_type].append(component)
                else:
                    self.components[used_for][comp_type].insert(0, component)
        if comp_type == "card_type":
            self.card_type_by_id[component.id] = component
            
    def unregister(self, component):
        comp_type = component.component_type
        used_for = component.used_for
        self.components[used_for][comp_type].remove(component)
        if component.component_type == "card_type":
            del self.card_type_by_id[component.id]

    def add_component_to_plugin(self, plugin_class_name, component_class):

        """Typical use case for this is when a plugin has a GUI
        component which obviously does not live inside libmnemosyne, and which
        needs to be added at a later stage.
        
        """
        
        for plugin in component_manager.get_all("plugin"):
            if plugin.__class__.__name__ == plugin_class_name:
                plugin.components.append(component_class)

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
        
    def deactivate_all(self):
        # First let plugins deactivate their subcomponents.
        for used_for in self.components:
            if "plugin" in self.components[used_for]:
                for component in self.components[used_for]["plugin"]:
                    component.deactivate()
        # Then do the other components.
        for used_for in self.components:
            for comp_type in self.components[used_for]:
                for component in self.components[used_for][comp_type]:
                    if not isinstance(component, type):
                        component.deactivate()
        self.components = {}
        self.card_type_by_id = {}
        
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

def main_widget():
    return component_manager.get_current("main_widget")

def review_widget():
    return component_manager.get_current("review_widget")

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

def _(text):
    return component_manager.get_current("translator").translate(text)
