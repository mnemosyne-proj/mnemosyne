#
# component_manager.py <Peter.Bienstman@UGent.be>
#


class ComponentManager():

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

       ======================   ===============================
       "database"               database instance
       "scheduler"              scheduler instance
       "filter"                 filter instance
       "card_type"              card_type instance
       "card_type_widget"       card_type_widget class,
                                used_for card_type class name
       "renderer"               renderer instance,
                                used_for card_type class name
       "ui_controller_review"   ui_controller_review instance
       "review_widget"          review_widget class
       ======================   ===============================
       
    Note: for widgets we store the class name as opposed to an instance,
    since creating widgets can be time consuming.
       
    TODO: plugin, function hook

    """

    def __init__(self):
        self.components = {} # { used_for : {type : [component]} }
        self.card_type_by_id = {}

    def register(self, type, component, used_for=None):
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

        if type in self.components[used_for]:
            return self.components[used_for][type]
        else:
            return []

    def get_current(self, type, used_for=None):

        """For component for which there can be only one active at one time."""

        if type in self.components[used_for]:
            return self.components[used_for][type][-1]
        else:
            return None


# The component manager needs to be accessed by many different parts of the
# library, so we hold it in a global variable.

component_manager = ComponentManager()


# Convenience functions, for easier access from the outside world.

def get_database():
    return component_manager.get_current("database")

def get_scheduler():
    return component_manager.get_current("scheduler")

def get_ui_controller_main():
    return component_manager.get_current("ui_controller_main")

def get_ui_controller_review():
    return component_manager.get_current("ui_controller_review")

def get_card_types():
    return component_manager.get_all("card_type")

def get_card_type_by_id(id):
    return component_manager.card_type_by_id[id]

def get_filters():
    return component_manager.get_all("filter")

