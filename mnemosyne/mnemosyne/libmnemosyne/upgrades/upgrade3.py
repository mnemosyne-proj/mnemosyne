#
# upgrade3.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.component import Component


class Upgrade3(Component):

    """Upgrade config from Pickle to Sqlite."""

    def run(self):
        if os.path.exists(os.path.join(self.config().config_dir, "config.db")):
            return
        if not os.path.exists(os.path.join(self.config().config_dir, "config")):
            return
        import cPickle
        old_config_file = \
            file(os.path.join(self.config().config_dir, "config"), "rb")
        try:    
            for key, value in cPickle.load(old_config_file).iteritems():
                if key not in ["import_format", "export_format"]:
                    self.config()[key] = value
        except EOFError:
            pass
        old_config_file.close() 
            