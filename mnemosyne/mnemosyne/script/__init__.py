#
# script <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne import Mnemosyne as MnemosyneParent
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class ScriptReviewWidget(ReviewWidget):

    def redraw_now(self):
        pass

class Mnemosyne(MnemosyneParent):

    def __init__(self, data_dir=None):
        MnemosyneParent.__init__(self, upload_science_logs=False,
            interested_in_old_reps=True)
        self.components.insert(0,
            ("mnemosyne.libmnemosyne.translators.gettext_translator",
             "GetTextTranslator"))
        self.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
        self.components.append(\
            ("mnemosyne.script", "ScriptReviewWidget"))
        self.initialise(data_dir)
