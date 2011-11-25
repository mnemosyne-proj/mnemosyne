#
# tip_after_starting_n_times.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component


class TipAfterStartingNTimes(Component):

    """Mixin class to show different tips after opening a dialog N times.

    'started_n_times_counter' is a string to be used in config to keep track
    of how many times the dialog was openened.

    'tip_after_n_times' is a dictionary like {2: "tip"}.
    
    The counter is not increased after the last tip has been reached, such
    that new tips can be added later.
    
    """

    started_n_times_counter = ""
    tip_after_n_times = {}
 
    def show_tip_after_starting_n_times(self):
        counter = self.config()[self.started_n_times_counter]
        if counter in self.tip_after_n_times:
            self.main_widget().show_information(\
                _(self.tip_after_n_times[counter]))
        if counter <= max(self.tip_after_n_times.keys()):
            self.config()[self.started_n_times_counter] = counter + 1
