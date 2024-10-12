#
# review_wdgt_cramming.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtWidgets, QtGui

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.review_wdgt import ReviewWdgt


class ReviewWdgtCramming(ReviewWdgt):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.grade_0_button.setText(_("Wrong"))
        self.grade_1_button.hide()
        self.line.hide()
        self.grade_2_button.hide()
        self.grade_3_button.hide()
        self.grade_4_button.hide()
        self.grade_5_button.setText(_("Right"))
        self.grade_5_button.setFocus()
        parent = self.parent()
        self.wrong = QtWidgets.QLabel("", parent.status_bar)
        self.unseen = QtWidgets.QLabel("", parent.status_bar)
        self.active = QtWidgets.QLabel("", parent.status_bar)
        self.font = QtGui.QFont()
        self.font.setPointSize(10)
        self.wrong.setFont(self.font)
        self.unseen.setFont(self.font)
        self.active.setFont(self.font)
        parent.clear_status_bar()
        parent.add_to_status_bar(self.wrong)
        parent.add_to_status_bar(self.unseen)
        parent.add_to_status_bar(self.active)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi(self)
        # Upon start, there will be a change event before the grade
        # buttons have been created.
        if hasattr(self, "grade_0_button"):
            self.grade_0_button.setText(_("Wrong"))
            self.grade_5_button.setText(_("Right"))
        QtWidgets.QWidget.changeEvent(self, event)

    def keyPressEvent(self, event):
        if self.review_controller().is_answer_showing():
            if event.key() in [QtCore.Qt.Key.Key_0, QtCore.Qt.Key.Key_1]:
                return self.grade_answer(0)
            elif event.key() in [QtCore.Qt.Key.Key_2, QtCore.Qt.Key.Key_3,
                QtCore.Qt.Key.Key_4, QtCore.Qt.Key.Key_5]:
                return self.grade_answer(5)
        super().keyPressEvent(event)

    def update_status_bar_counters(self):
        wrong_count, unseen_count, active_count = \
                   self.review_controller().counters()
        self.wrong.setText(_("Wrong:") + " %d " % wrong_count)
        self.unseen.setText(_("Unseen:") + " %d " % unseen_count)
        self.active.setText(_("Active:") + " %d " % active_count)
