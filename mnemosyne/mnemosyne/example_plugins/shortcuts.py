#
# shortcuts.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.pyqt_ui.review_wdgt import ReviewWdgt


class MyReviewWdgt(ReviewWdgt):

    def __init__(self, **kwds):
        super().__init__(**kwds)
    
        self.auto_focus_grades = False

        # Change shortcuts for the grade buttons.
        self.grade_0_button.setShortcut("q")
        self.grade_1_button.setShortcut("w")
        self.grade_2_button.setShortcut("e")
        self.grade_3_button.setShortcut("r")
        self.grade_4_button.setShortcut("t")
        self.grade_5_button.setShortcut("y")

        # Some more examples.
        
        #self.grade_0_button.setShortcut("Enter") # Numerical keypad
        #self.grade_1_button.setShortcut("Space")
        #self.grade_2_button.setShortcut("Return") 


class ShortcutsPlugin(Plugin):

    name = "Custom shortcuts"
    description = "Customise review widget shortcuts."
    components = [MyReviewWdgt]


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(ShortcutsPlugin)
