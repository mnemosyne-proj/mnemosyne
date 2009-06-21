#
# current_card.py <Peter.Bienstman@UGent.be>
#

import time

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.statistics_page import StatisticsPage

DAY = 24 * 60 * 60 # Seconds in a day.


class CurrentCard(StatisticsPage):

    name = _("Current card")
        
    def prepare(self, variant):
        card = self.ui_controller_review().card
        self.data = """<html<body>
        <style type="text/css">
        table { height: 100%;
                margin-left: auto; margin-right: auto;
                text-align: center}
        body  { background-color: white;
                margin: 0;
                padding: 0;
                border: thin solid #8F8F8F; }
        </style></head><table><tr><td>"""
        if not card:
            self.data += _("No current card.")
        elif card.grade == -1:
            self.data += _("Unseen card, no statistics available yet.")
        else:
            self.data += _("Grade") + ": %d<br>" % card.grade
            self.data += _("Easiness") + ": %1.2f<br>" % card.easiness
            self.data += _("Repetitions") + ": %d<br>" \
                % (card.acq_reps + card.ret_reps)
            self.data += _("Lapses") + ": %d<br>" % card.lapses
            self.data += _("Interval") + ": %d<br>" \
                % (card.interval / DAY)            
            self.data += _("Next repetition") + ": %s<br>" \
                % time.strftime("%B %d, %Y", time.gmtime(card.next_rep))
        self.data += "</td></tr></table></body></html>"
