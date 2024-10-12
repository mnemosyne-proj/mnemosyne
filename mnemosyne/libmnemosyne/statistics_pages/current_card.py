#
# current_card.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.statistics_page import HtmlStatisticsPage

DAY = 24 * 60 * 60 # Seconds in a day.

class CurrentCard(HtmlStatisticsPage):

    name = _("Current card")

    def prepare_statistics(self, variant):
        card = self.review_controller().card
        self.html = """<html<body>
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
            self.html += _("No current card.")
        elif card.grade == -1:
            self.html += _("Unseen card, no statistics available yet.")
        else:
            self.html += _("Grade") + ": %d<br>" % card.grade
            self.html += _("Easiness") + ": %1.2f<br>" % card.easiness
            self.html += _("Learning repetitions") + ": %d<br>" \
                % card.acq_reps
            self.html += _("Review repetitions") + ": %d<br>" \
                % card.ret_reps
            self.html += _("Lapses") + ": %d<br>" % card.lapses
            self.html += _("Last repetition") + ": %s<br>" \
                % self.scheduler().last_rep_to_interval_string(card.last_rep)
            self.html += _("Next repetition") + ": %s<br>" \
                % self.scheduler().next_rep_to_interval_string(card.next_rep)
            self.html += _("Average thinking time (secs)") + ": %d<br>" \
                % self.database().average_thinking_time(card)
            self.html += _("Total thinking time (secs)") + ": %d<br>" \
                % self.database().total_thinking_time(card)
        self.html += "</td></tr></table></body></html>"
