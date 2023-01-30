#
# configuration.py <Peter.Bienstman@gmail.com>
#

import os

from mnemosyne.libmnemosyne.hook import Hook


class AndroidConfiguration(Hook):

    used_for = "configuration_defaults"

    def run(self):
        for key, value in \
            list({"server_for_sync_as_client": "",
             "port_for_sync_as_client": 8512,
             "username_for_sync_as_client": "",
             "password_for_sync_as_client": "",
             "remember_password_for_sync_as_client": True,
            }.items()):
            self.config().setdefault(key, value)
