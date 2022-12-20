#
# script <Peter.Bienstman@gmail.com>
#

import os.path

from mnemosyne.libmnemosyne import Mnemosyne as MnemosyneParent
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget

class ScriptReviewWidget(ReviewWidget):

    def redraw_now(self):
        pass


class ScriptMainWidget(MainWidget):

    def __init__(self, component_manager):
        super().__init__(component_manager)
        self.q_and_a = None

    def show_question(self, question, option0, option1, option2):
        print((question, option0, option1, option2))
        if self.q_and_a is not None:
            for q, a in self.q_and_a.items():
                if question.startswith(q):
                    return a
        raise NotImplementedError


class Mnemosyne(MnemosyneParent):

    def __init__(self, data_dir=None, filename=None):
        MnemosyneParent.__init__(self, upload_science_logs=False,
            interested_in_old_reps=True)
        self.components.insert(0,
            ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator",
             "GetTextGuiTranslator"))
        self.components.append(\
            ("mnemosyne.script", "ScriptMainWidget"))
        self.components.append(\
            ("mnemosyne.script", "ScriptReviewWidget"))
        self.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne.script", "ScriptReviewWidget")]
        self.gui_for_component["CramRecent"] = \
            [("mnemosyne.script", "ScriptReviewWidget")]
        self.gui_for_component["CramAll"] = \
            [("mnemosyne.script", "ScriptReviewWidget")]  
        self.gui_for_component["NewOnly"] = \
            [("mnemosyne.script", "ScriptReviewWidget")]    
        if data_dir is not None:
            data_dir = os.path.abspath(data_dir)
        self.initialise(data_dir, filename=filename)

