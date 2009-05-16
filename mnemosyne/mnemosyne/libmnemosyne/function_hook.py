#
# function_hook.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class FunctionHook(Component):

    """Function hooks are used by registering an instance of this class as
    component of type function_hook, with the "used_for" argument any of the
    following hook points:
    
       ======================   ===============================
       "after_load"             in database.load
       "create_new_cards"       in default_main_controller
       "update_related_cards"   in default_main_controller
       ======================   ===============================

    It is the 'run' method that will get called at the corresponding point
    in the program.
    
    """

    component_type = "function_hook"
    
    def run(self):
        raise NotImplementedError

