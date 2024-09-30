#
# shortcuts.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.pyqt_ui.review_wdgt import ReviewWdgt


class MyReviewWdgt(ReviewWdgt):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        # Map Q to grade 0
        self.key_to_grade_map[QtCore.Qt.Key.Key_Q] = 0


class ShortcutsPlugin(Plugin):

    name = "Custom shortcuts"
    description = "Customise review widget shortcuts."
    gui_for_component = {"ScheduledForgottenNew" :
        [("shortcuts", "MyReviewWdgt")]}
    gui_for_component = {"NewOnly" :
        [("shortcuts", "MyReviewWdgt")]}
    gui_for_component = {"CramAll" :
        [("shortcuts", "MyReviewWdgt")]}
    gui_for_component = {"CramRecent" :
        [("shortcuts", "MyReviewWdgt")]}
    supported_API_level = 3


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
plugin = register_user_plugin(ShortcutsPlugin)
