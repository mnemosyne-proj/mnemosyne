##############################################################################
#
# plugin.py <Peter.Bienstman@UGent.be>
#
##############################################################################



# TODO: update comments

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

class Plugin(Component):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, name, description=""):
        
        self.name         = name
        self.description  = description
        self.active       = False
        
        plugin_manager.register("plugin", self)



        
    ##########################################################################
    #
    # activate
    #
    #  Code that needs to run once on startup goes here, e.g. making sure
    #  that a card type shows up in 'Add new cards'.
    #
    ##########################################################################
    
    def activate(self):
        
        self.active = True


    
    ##########################################################################
    #
    # deactivate
    #
    #  Code that needs to run once on shutdown, e.g. making sure that a card
    #  type no longer shows up in 'Add new cards'.
    #
    ##########################################################################
    
    def deactivate(self):
        
        self.active = False
