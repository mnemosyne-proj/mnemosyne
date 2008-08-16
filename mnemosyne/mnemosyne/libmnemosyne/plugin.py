##############################################################################
#
# plugin.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.component_manager import component_manager



##############################################################################
#
# Plugin
#
#   A plugin is a component which can be activated and deactivated by the
#   user when the program is running. In addition to the standard
#   implementation of these (de)activation routines below, a plugin
#   typically (un)register one or more other components (or 'self', if one
#   uses multiple inheritance).
#
##############################################################################

class Plugin(Component):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, name, description):

        self.name         = name
        self.description  = description
        self.active       = False

        component_manager.register("plugin", self)



    ##########################################################################
    #
    # activate
    #
    ##########################################################################

    def activate(self):

        self.active = True



    ##########################################################################
    #
    # deactivate
    #
    ##########################################################################

    def deactivate(self):

        self.active = False
