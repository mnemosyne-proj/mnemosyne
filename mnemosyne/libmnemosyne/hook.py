#
# hook.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component


class Hook(Component):

    """Function hooks are used by registering an instance of this class as
    component of type hook, with the 'used_for' argument any of the following
    hook points:

       =====================================   ===============================
       'after_load'                            in database.load
       'after_backup'                          in database.backup
       'before_unload'                         in database.unload
       'configuration_defaults'                in configuration.set_defaults
       'before_repetititon'                    in SM2_mnemosyne.grade_answer
                                               extra argument: card
       'after_repetititon'                     in SM2_mnemosyne.grade_answer
                                               extra argument: card
       'dynamically_create_media_files'        in SQLite_sync
                                               extra argument: data
       'delete_unused_media_files'             in SQLite_sync
       'preprocess_cloze'                      in cloze.py
       'postprocess_q_a_cloze'                 in cloze.py
       'at_rollover'                           in default_controller.py
       =====================================   ===============================

    It is the 'run' method that will get called at the corresponding point
    in the program.

    """

    component_type = "hook"

    def run(self):
        raise NotImplementedError
