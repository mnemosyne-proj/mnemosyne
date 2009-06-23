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
        self.components = {} # {used_for: {type: [component]} }
        self.card_type_by_id = {}

    def register(self, component, in_front=False):
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
        
        for plugin in self.get_all("plugin"):
            if plugin.__class__.__name__ == plugin_class_name:
                plugin.components.append(component_class)

    def get_all(self, comp_type, used_for=None):
        
        """For components for which there can be many active at once."""

        if used_for == None or isinstance(used_for, str):
            try:
                return self.components[used_for][comp_type]
            except:
                return []

        # See if there is a component registered for the exact type.
        try:
            return self.components[used_for][comp_type]
        except:
            # See if there is a component registered for the parent class.
            class_keys = [key for key in self.components.keys() if \
                          not isinstance(key, str) and not (key == None)]
            if isinstance(used_for, tuple):
                for key in class_keys:
                    if issubclass(used_for[0], key[0]) and \
                       issubclass(used_for[1], key[1]):
                        try:
                            return self.components[key][comp_type]
                        except:
                            return []
                return []
            else:
                for key in class_keys:
                    if issubclass(used_for, key):
                        try:
                            return self.components[key][comp_type]
                        except:
                            return []
                return []
        
    def get_current(self, comp_type, used_for=None):
        
        """For components for which there can be only one active at any
        time.

        """

        all = self.get_all(comp_type, used_for)
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


# A component manager stores the entire session state of a user through the
# different components it registers. To enable multiple users to use
# libmnemosyne simultaneously, we store a component manager instance for each
# user.

_component_managers = {}

def new_component_manager():
    return ComponentManager()

def register_component_manager(component_manager, user_id):
    global _component_managers
    _component_managers[user_id] = component_manager
    
def unregister_component_manager(user_id):
    global _component_managers
    del _component_managers[user_id]
