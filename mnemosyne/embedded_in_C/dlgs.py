#
# dlgs.py <Peter.Bienstman@gmail.com>
#

import _dlgs as _
import mnemosyne.libmnemosyne.ui_components.dialogs as dialogs


class AddCardsDlg(dialogs.AddCardsDialog):

    def activate(self):
        _.add_cards_dlg_activate()


class EditCardDlg(dialogs.EditCardDialog):
    
    def __init__(self, card, component_manager, allow_cancel=True):
        self.card = card
        self.allow_cancel = allow_cancel

    def activate(self):
        _.edit_card_dlg_activate(self.card.id, self.allow_cancel)

        
class ActivateCardsDlg(dialogs.ActivateCardsDialog):

    def activate(self):
        _.activate_cards_dlg_activate()
        
    
class BrowseCardsDlg(dialogs.BrowseCardsDialog):
    
    def activate(self):
        _.browse_cards_dlg_activate()


class CardAppearanceDlg(dialogs.CardAppearanceDialog):
    
    def activate(self):
        _.card_appearance_dlg_activate()
        
    
class ActivatePluginsDlg(dialogs.ActivatePluginsDialog):
    
    def activate(self):
        _.activate_plugins_dlg_activate()


class ManageCardTypesDlg(dialogs.ManageCardTypesDialog):
    
    def activate(self):
        _.manage_card_types_dlg_activate()


class StatisticsDlg(dialogs.StatisticsDialog):

    def activate(self):
        _.statistics_dlg_activate()


class ConfigurationDlg(dialogs.ConfigurationDialog):

    def activate(self):
        _.configuration_dlg_activate()


class SyncDlg(dialogs.SyncDialog):
    
    def activate(self):
        _.sync_dlg_activate()
