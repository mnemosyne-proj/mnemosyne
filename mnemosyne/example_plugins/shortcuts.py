#
# shortcuts.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.pyqt_ui.review_wdgt import ReviewWdgt


class MyReviewWdgt(ReviewWdgt):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        # Map Q to grade 0
        self.key_to_grade_map[QtCore.Qt.Key_Q] = 0


class ShortcutsPlugin(Plugin):

    name = "Custom shortcuts"
    description = "Customise review widget shortcuts."
    supported_API_level = 2

    def activate(self, **kwds):
        super().activate(**kwds)
        # These add our widget to the end of the list, which is the correct
        # position, as it should be initialised last.
        self.component_manager.add_gui_to_component(\
            "ScheduledForgottenNew", MyReviewWdgt)
        self.component_manager.add_gui_to_component(\
            "NewOnly", MyReviewWdgt)
        self.component_manager.add_gui_to_component(\
            "CramAll", MyReviewWdgt)
        self.component_manager.add_gui_to_component(\
            "CramRecent", MyReviewWdgt)

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
plugin = register_user_plugin(ShortcutsPlugin)
