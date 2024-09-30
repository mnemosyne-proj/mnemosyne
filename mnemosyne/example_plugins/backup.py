#
# backup.py <Peter.Bienstman@gmail.com>
#

import os
import sqlite3

from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.plugin import Plugin


class BackupHook(Hook):

    used_for = "after_backup"

    def run(self, backup_name):
        # Upload regular backup to a server.
        os.system("scp %s my.safe.server.com:" % backup_name)
        # Dump database to a text file (requires Python 2.6).
        with open('dump.sql', 'w') as f:
            for line in self.database().con.iterdump():
                f.write('%s\n' % line)


class BackupPlugin(Plugin):
    
    name = "Extra backup"
    description = "Move your backups to a safe place."   
    components = [BackupHook]
    supported_API_level = 3
      

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(BackupPlugin)


