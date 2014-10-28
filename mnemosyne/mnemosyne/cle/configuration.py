#
# configuration.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.hook import Hook


class AndroidConfiguration(Hook):

    used_for = "configuration_defaults"

    def run(self):
        for key, value in \
            {"server_for_sync_as_client": "",
             "port_for_sync_as_client": 8512,
             "username_for_sync_as_client": "",
             "password_for_sync_as_client": "",
            }.items():
            self.config().setdefault(key, value)
