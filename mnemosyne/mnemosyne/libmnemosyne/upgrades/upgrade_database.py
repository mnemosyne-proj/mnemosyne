#
# upgrade_database.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class UpgradeDatabase(Component):

    def run(self, file_to_upgrade):
        for format in self.component_manager.get_all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                format.do_import(file_to_upgrade)
                self.review_controller().reset()
                    

