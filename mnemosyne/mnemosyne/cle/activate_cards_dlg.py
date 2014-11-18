#
# activate_cards_dlg.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_components.dialogs import ActivateCardsDialog


class ActivateCardsDlg(ActivateCardsDialog):
    
    def __init__(self, component_manager):
        ActivateCardsDialog.__init__(self, component_manager)    
        
    def activate(self):
        self.criteria_by_name = {}
        active_set_name = ""
        active_criterion = self.database().current_criterion()
        for criterion in self.database().criteria():
            if criterion._id != 1:
                self.criteria_by_name[criterion.name] = criterion
                if criterion == active_criterion:
                    active_set_name = criterion.name
        self.component_manager.android.showActivateCardsDialog(\
            sorted(self.criteria_by_name.keys()), active_set_name)
        
    def set_criterion_with_name(self, criterion_name):
        print 'setting', criterion_name
        self.database().set_current_criterion(self.criteria_by_name[criterion_name])
        