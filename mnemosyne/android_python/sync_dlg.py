#
# sync_dlg.py <Peter.Bienstman@UGent.be>
#

import _dialogs

from mnemosyne.libmnemosyne.ui_components.dialogs import SyncDialog


class SyncDlg(SyncDialog):

    def __init__(self, component_manager):
        SyncDialog.__init__(self, component_manager)

    def activate(self):
        SyncDialog.activate(self)
        _dialogs.sync_dlg_activate()
