#
# Widget to preview set of sister cards <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.review_wdgt import QAOptimalSplit
from mnemosyne.pyqt_ui.ui_preview_cards_dlg import Ui_PreviewCardsDlg


class PreviewCardsDlg(QtWidgets.QDialog, Component, QAOptimalSplit,
                      Ui_PreviewCardsDlg):

    page_up_down_signal = QtCore.pyqtSignal(int)
    UP = 0
    DOWN = 1

    def __init__(self, cards, tag_text, **kwds):

        """We need to provide tag_text explicitly, since it's possible that
        the cards have not yet been added to the database.

        """
        super().__init__(**kwds)
        self.setupUi(self)
        # Needed to make sure we can process e.g. escape keys. Not yet perfect
        # though, as clicking on the html widget eats those keys again.
        self.question.setFocusProxy(self)
        self.answer.setFocusProxy(self)
        QAOptimalSplit.setup(self)
        self.used_for_reviewing = False
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.tag_text = tag_text
        self.cards = cards
        self.index = 0
        state = self.config()["preview_cards_dlg_state"]
        if state:
            self.restoreGeometry(state)
        self.update_dialog()

    def keyPressEvent(self, event):

        """When this dialog is called from the card browser, PageUp and
        PageDown keys can be used to move the previous/next card in the list.

        """

        if event.key() == QtCore.Qt.Key.Key_PageUp:
            self.page_up_down_signal.emit(self.UP)
        elif event.key() == QtCore.Qt.Key.Key_PageDown:
            self.page_up_down_signal.emit(self.DOWN)
        # Note QtWidgets.QWidget.keyPressEvent(self, event) does not seem to work,
        # so we handle the most common keypresses here too.
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.reject()
        if event.key() in [QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return]:
            self.accept()
        else:
            QtWidgets.QWidget.keyPressEvent(self, event)

    def update_dialog(self):
        self.question_label.setText(_("Question: ") + self.tag_text)
        if len(self.cards) == 1:
            self.previous_button.setVisible(False)
            self.next_button.setVisible(False)
            self.fact_view_name.setVisible(False)
        card = self.cards[self.index]
        stored = self.config()["QA_split"]
        self.config()["QA_split"] = "fixed"
        self.set_question(card.question())
        self.set_answer(card.answer())
        self.reveal_question()
        self.reveal_answer()
        self.config()["QA_split"] = stored
        self.fact_view_name.setText(_(card.fact_view.name) + " (" + \
            str(self.index + 1) + "/" + str(len(self.cards)) + ")")
        self.previous_button.setEnabled(self.index != 0)
        self.next_button.setEnabled(self.index != len(self.cards) - 1)

    def previous(self):
        self.review_widget().stop_media()
        self.index -= 1
        self.update_dialog()

    def next(self):
        self.review_widget().stop_media()
        self.index += 1
        self.update_dialog()

    def _store_state(self):
        self.config()["preview_cards_dlg_state"] = self.saveGeometry()

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self.review_widget().stop_media()
        self._store_state()

    def accept(self):
        # 'accept' does not generate a close event.
        self.review_widget().stop_media()
        self._store_state()
        return QtWidgets.QDialog.accept(self)

    def reject(self):
        self.review_widget().stop_media()
        self._store_state()
        QtWidgets.QDialog.reject(self)
