#
# tip_after_starting_n_times.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.pyqt_ui.tip_dlg import TipDlg
from mnemosyne.libmnemosyne.gui_translator import _
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
            tip_dlg = TipDlg(component_manager=self.component_manager)
            tip_dlg.setWindowTitle(_("Mnemosyne"))
            tip_dlg.show_tips.hide()
            tip_dlg.previous_button.hide()
            tip_dlg.next_button.hide()
            tip_dlg.tip_label.setText(_(self.tip_after_n_times[counter]))
            tip_dlg.closeEvent = lambda event : event.accept()
            tip_dlg.exec()
        if counter <= max(self.tip_after_n_times.keys()):
            self.config()[self.started_n_times_counter] = counter + 1
