#
# upgrade_beta_7.py <Peter.Bienstman@UGent.be>
#

import sqlite3

from mnemosyne.libmnemosyne.component import Component


class UpgradeBeta7(Component):
            
    def run(self):
        try:
            self.database().con.executescript("""
                create index i_cards_2 on cards (fact_view_id);
                create index i_tags_for_card_2 on tags_for_card (_tag_id);""")
        except sqlite3.OperationalError:
            pass

