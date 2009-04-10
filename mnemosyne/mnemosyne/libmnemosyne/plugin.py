#
# plugin.py <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from mnemosyne.libmnemosyne.component_manager import config
from mnemosyne.libmnemosyne.component_manager import database
from mnemosyne.libmnemosyne.component_manager import component_manager
from mnemosyne.libmnemosyne.component_manager import ui_controller_main


class Plugin(object):

    """A plugin is a component which can be activated and deactivated by the
    user when the program is running.  Typically, plugins derive from both 
    Plugin and the component they implement, and set the 'provides' class 
    variable to the string describing the component type.
    
    """

    name = ""
    description = ""
    provides = ""
    show_in_first_run_wizard = False
    activation_message = ""
        
    def __init__(self):
        assert self.name and self.description, \
            "A Plugin needs a name and description."
        
    def activate(self):
        if self.activation_message and ui_controller_main().widget:
            ui_controller_main().widget.information_box(\
                self.activation_message)
        component_manager.register(self.provides, self)
        config()["active_plugins"].add(self.__class__)

    def deactivate(self):
        if self.provides == "card_type":
            for card_type in database().card_types_in_use():
                if issubclass(card_type.__class__, self.__class__):
                    ui_controller_main().widget.information_box(\
        _("Cannot deactivate, this card type or a clone of it is in use."))
                    return False  
        component_manager.unregister(self.provides, self)
        config()["active_plugins"].remove(self.__class__)
        return True
