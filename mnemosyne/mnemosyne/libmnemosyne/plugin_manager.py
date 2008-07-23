##############################################################################
#
# plugin_manager.py <Peter.Bienstman@UGent.be>
#
##############################################################################



##############################################################################
#
# PluginManager
#
##############################################################################

class PluginManager():

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self):
        
        self.plugins = {}



    ##########################################################################
    #
    # register_plugin
    #
    ##########################################################################

    def register_plugin(self, type, plugin):

        if not self.plugins.has_key(type):
            self.plugins[type] = [plugin]
        else:
            if plugin not in self.plugins[type]:
                self.plugins[type].append(plugin)


            
    ##########################################################################
    #
    # unregister_plugin
    #
    ##########################################################################

    def unregister_plugin(self, type, plugin):

        if not plugin.can_be_unregistered:
            
            print "Plugin", plugin, "cannot be unregistered."
            return

        self.plugins[type].remove(plugin)



    ##########################################################################
    #
    # get_all_plugins
    #
    #   For resources for which there can be many active at the same
    #   time, like card types, filters, function hooks, ...
    #
    ##########################################################################
    
    def get_all_plugins(self, type):
        
        return self.plugins[type]


    
    ##########################################################################
    #
    # get_current_plugin
    #
    #   For resources for which there can be only on active at the same
    #   time, like schedule, database ... The idea is that the last one
    #   added takes preference. This means that e.g. the default scheduler
    #   needs to be registered first and best has 'can_be_unregistered'
    #   set to False.
    #
    ##########################################################################

    def get_current_plugin(self, type):        
        return self.plugins[type][-1]


##############################################################################
#
# The plugin manager needs to be accessed by many different parts of the
# library, so we hold it in a global variable.
#
##############################################################################

plugin_manager = PluginManager()



##############################################################################
#
# Convenience functions, for easier access from the outside.
#
##############################################################################

def get_database():
    return plugin_manager.get_current_plugin("database")

def get_scheduler():
    return plugin_manager.get_current_plugin("scheduler")

def get_ui_controller():
    return plugin_manager.get_current_plugin("ui_controller")

def get_card_types():
    return plugin_manager.get_all_plugins("card_type")

def get_card_type(type): # TODO: still needed?
    for t in get_card_types():
        if isinstance(t, type):
            return t
    
