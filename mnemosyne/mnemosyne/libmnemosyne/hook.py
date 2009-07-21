#
# hook.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Hook(Component):

    """Function hooks are used by registering an instance of this class as
    component of type hook, with the "used_for" argument any of the following
    hook points:
    
       ========================   ===============================
       "after_load"               in database.load
       "after_backup"             in database.backup
       "before_unload"            in database.unload
       "configuration_defaults"   in configuration.set_defaults
       "before_repetititon"       in SM2_mnemosyne.grade_answer
                                  extra argument: card
       "after_repetititon"        in SM2_mnemosyne.grade_answer
                                  extra argument: card
       ========================   ===============================

    It is the 'run' method that will get called at the corresponding point
    in the program.
    
    """

    component_type = "hook"
    
    def run(self):
        raise NotImplementedError

