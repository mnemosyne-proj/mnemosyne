##############################################################################
#
# component_manager.py <Peter.Bienstman@UGent.be>
#
##############################################################################



##############################################################################
#
# ComponentManager
#
#   Manages the different components. Each component belongs to a type
#   (database, scheduler, card_type, card_type_widget, ...).
#
#   The component manager can also store relationships between components,
#   e.g. a card_type_widget is used for a certain card_type.
#
#   For certain components, many can be active at the same time (card types,
#   filters, function hooks, ...). For others, there can be only on active
#   at the same time, like schedule, database ... The idea is that the last
#   one registered takes preference. This means that e.g. the default
#   scheduler needs to be registered first.
#
##############################################################################

class ComponentManager():

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self):
        
        self.components = {} # { used_for : {type : [component]} }



    ##########################################################################
    #
    # register
    #
    ##########################################################################

    def register(self, type, component, used_for=None):

        if not self.components.has_key(used_for):
            self.components[used_for] = {}

        if not self.components[used_for].has_key(type):
            self.components[used_for][type] = [component]
        else:
            if component not in self.components[type]:
                self.components[used_for][type].append(component)


            
    ##########################################################################
    #
    # unregister
    #
    ##########################################################################

    def unregister(self, type, component, used_for=None):

        self.components[used_for][type].remove(component)



    ##########################################################################
    #
    # get_all
    #
    #   For components for which there can be many active at once.
    #
    ##########################################################################
    
    def get_all(self, type, used_for=None):

        if type in self.components[used_for]:
            return self.components[used_for][type]
        else:
            return []


    
    ##########################################################################
    #
    # get_current
    #
    #   For component for which there can be only one active at one time.
    #
    ##########################################################################

    def get_current(self, type, used_for=None):

        if type in self.components[used_for]:
            return self.components[used_for][type][-1]
        else:
            return None




##############################################################################
#
# The component manager needs to be accessed by many different parts of the
# library, so we hold it in a global variable.
#
##############################################################################

print "Registering component manager"

component_manager = ComponentManager()



##############################################################################
#
# Convenience functions, for easier access from the outside world.
#
# Keep these?
#
##############################################################################

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

def get_card_type_by_id(id): # TODO: speed up with dict?
    for t in get_card_types():
        if t.id == id:
            return t
    
def get_fact_filters():
    return component_manager.get_all("fact_filter")
