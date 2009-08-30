#
# upgrade_config.py <Peter.Bienstman@UGent.be>
#

import os
import shutil

from mnemosyne.libmnemosyne.component import Component


class UpgradeConfig(Component):

    def run(self):
        # Move old plugins out of the way.
        plugin_dir = os.path.join(self.config().basedir, "plugins")
        new_plugin_dir = os.path.join(self.config().basedir, "plugins_1.x")            
        if os.path.exists(plugin_dir):
            shutil.move(plugin_dir, new_plugin_dir)
