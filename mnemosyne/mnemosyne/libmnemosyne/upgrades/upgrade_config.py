#
# upgrade_config.py <Peter.Bienstman@UGent.be>
#

import os

from mnemosyne.libmnemosyne.component import Component


class UpgradeConfig(Component):

    def run(self):

        """Upgrade from 1.x to 2.0."""

        config = self.config()
        
        if config["path"].endswith(".mem"):
            # Move old plugins out of the way.
            plugin_dir = os.path.join(self.config().basedir, "plugins")
            new_plugin_dir = os.path.join(self.config().basedir, "plugins_1.x")            
            if os.path.exists(plugin_dir):
                os.rename(plugin_dir, new_plugin_dir)
                os.mkdir(plugin_dir)
            # Migrate settings.
            config["grade_0_cards_in_hand"] = config["grade_0_items_at_once"]
            for card_type in self.card_types():
                card_type.renderer().set_property("font", config["QA_font"],
                                                      card_type)
            if config["left_align"]:
                for card_type in self.card_types():                
                    card_type.renderer().set_property(\
                        "alignment", "left", card_type)
            del config["hide_toolbar"]
            del config["QA_font"]
            del config["list_font"]
            del config["left_align"]
            del config["non_latin_font_size_increase"]
            del config["check_duplicates_when_adding"]
            del config["allow_duplicates_in_diff_cat"]
            del config["grade_0_items_at_once"]
            del config["last_add_vice_versa"]
            del config["last_add_category"]
            del config["3_sided_input"]
            del config["column_0_width"]
            del config["column_1_width"]
            del config["column_2_width"]
            del config["sort_column"]            
            del config["sort_order"]
            del config["locale"]
            config["upload_science_logs"] = config["upload_logs"]
            del config["upload_logs"]
            del config["upload_server"]
            # Migrate latex settings.
            setting_for_file = {"dvipng": "dvipng",
                                "preamble": "latex_preamble",
                                "postamble": "latex_postamble"}
            for filename, setting in setting_for_file.iteritems():
                full_filename = os.path.join(config.basedir, "latex", filename)
                config[setting] = ""
                for line in file(full_filename):
                    config[setting] += line
                os.rename(full_filename, full_filename + ".NO_LONGER_USED")
            os.rename(os.path.join(config.basedir, "latex"),
                      os.path.join(config.basedir, "latex.NO_LONGER_USED"))
            
                     
            