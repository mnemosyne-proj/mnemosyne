#
# upgrade_beta_8.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.component import Component

forbidden_lines = [
"# The following setting can be set to False to speed up the syncing process on",
"# e.g. mobile clients where the media files don't get edited externally.",
"check_for_edited_local_media_files = True",
"# The number of repetitions that need to happen before autosave.",
"# Setting this to 1 means saving after every repetition.",
"save_after_n_reps = 1"
]


class UpgradeBeta8(Component):

    def run(self):
        config_file_name = os.path.join(self.config().config_dir, "config.py")
        lines = []
        for line in file(config_file_name):
            if line.strip() not in forbidden_lines:
                lines.append(line)
        new_config_file = file(config_file_name, "w")
        for line in lines:
            print >> new_config_file, line,


