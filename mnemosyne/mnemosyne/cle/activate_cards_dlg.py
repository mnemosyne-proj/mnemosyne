#
# activate_cards_dlg.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog


class ActivateCardsDlg(ActivateCardsDialog): 
        
    def activate(self):
        self.criteria_by_name = {}
        active_set_name = ""
        active_criterion = self.database().current_criterion()
        for criterion in self.database().criteria():
            if criterion._id != 1:
                self.criteria_by_name[criterion.name.encode("utf-8")] = criterion
                if criterion == active_criterion:
                    active_set_name = criterion.name.encode("utf-8")  
        self.component_manager.android.showActivateCardsDialog(\
            "____".join(sorted(self.criteria_by_name.keys())), active_set_name, self)
        
    def set_criterion_with_name(self, criterion_name):
        self.database().set_current_criterion(self.criteria_by_name[criterion_name])
        