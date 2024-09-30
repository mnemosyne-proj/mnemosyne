#
# activate_cards_dlg.py <Peter.Bienstman@gmail.com>
#

import _dialogs

from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog


class ActivateCardsDlg(ActivateCardsDialog):

    def activate(self):
        ActivateCardsDialog.activate(self)
        self.criteria_by_name = {}
        active_set_name = ""
        active_criterion = self.database().current_criterion()
        for criterion in self.database().criteria():
            if criterion._id != 1:
                self.criteria_by_name[criterion.name] = criterion
                if criterion == active_criterion:
                    active_set_name = criterion.name
        _dialogs.activate_cards_dlg_activate(\
            "____".join(sorted(self.criteria_by_name.keys())), active_set_name)
