##############################################################################
#
# component_manager.py <Peter.Bienstman@UGent.be>
#
##############################################################################


#TODO: document, list typical types


##############################################################################
#
# ComponentManager
#
##############################################################################

class ComponentManager():

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self):
        
        self.components = {} # {type : [component]}



    ##########################################################################
    #
    # register
    #
    ##########################################################################

    def register(self, type, component):

        if not self.components.has_key(type):
            self.components[type] = [component]
        else:
            if component not in self.components[type]:
                self.components[type].append(component)


            
    ##########################################################################
    #
    # unregister
    #
    ##########################################################################

    def unregister(self, type, component):

        self.components[type].remove(component)



    ##########################################################################
    #
    # get_all
    #
    #   For components for which there can be many active at the same
    #   time, like card types, filters, function hooks, ...
    #
    ##########################################################################
    
    def get_all(self, type):

        if type in self.components:
            return self.components[type]
        else:
            return []


    
    ##########################################################################
    #
    # get_current
    #
    #   For component for which there can be only on active at the same
    #   time, like schedule, database ... The idea is that the last one
    #   added takes preference. This means that e.g. the default scheduler
    #   needs to be registered first.
    #
    ##########################################################################

    def get_current(self, type):

        if type in self.components:
            return self.components[type][-1]
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
    
