##############################################################################
#
# plugin.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from plugin_manager import plugin_manager


# rename: 'can be unregistered' to 'managed by'

##############################################################################
#
# Plugin
#
#  Note that a plugin can be registered, but not yet activated. I.e. a
#  card type for an exotic language will not show up in the drop down box
#  of available card types unless the card type is activated in the GUI
#  through the plugin manager widget.
#
#  A plugin has a type, name and description, e.g.
#
#    type = "card_type"
#    name = "Foreign word with pronunciation"
#    description = "Three sided card type for memorising vocabulary in non-
#                   latin script."
#
##############################################################################

class Plugin:

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, type, name, description="", can_be_unregistered=True):
        
        self.type                = type
        self.name                = name
        self.description         = description
        self.active              = False
        self.can_be_unregistered = can_be_unregistered



    ##########################################################################
    #
    # register
    #
    #  TODO: move to constructor?
    #
    ##########################################################################
    
    def register(self):
        plugin_manager.register(self.type, self)


    
    ##########################################################################
    #
    # unregister
    #
    ##########################################################################
    
    def unregister(self):
        plugin_manager.unregister(self.type, self)


        
    ##########################################################################
    #
    # activate
    #
    #  Code that needs to run once on startup, e.g. making sure that a card
    #  type shows up in 'Add new cards'.
    #
    ##########################################################################
    
    def activate(self):
        self.active = True


    
    ##########################################################################
    #
    # run
    #
    #  Code that needs to run several times, e.g. for Filters or
    #  FunctionHooks.
    #
    ##########################################################################
    
    def run(self):
        raise NotImplementedError()


    
    ##########################################################################
    #
    # deactivate
    #
    #  Code that needs to run once on shutdown, e.g. making sure that a card
    #  type no longer shows up in 'Add new cards'.
    #
    ##########################################################################
    
    def deactivate(self):
        if self.can_be_unregistered:
            self.active = False
