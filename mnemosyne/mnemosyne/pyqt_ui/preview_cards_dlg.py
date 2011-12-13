#
# Widget to preview set of sister cards <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.review_wdgt import determine_stretch_factor
from mnemosyne.pyqt_ui.ui_preview_cards_dlg import Ui_PreviewCardsDlg


class PreviewCardsDlg(QtGui.QDialog, Ui_PreviewCardsDlg, Component):

    page_up_down_signal = QtCore.pyqtSignal(int)
    UP = 0
    DOWN = 1

    def __init__(self, component_manager, cards, tag_text, parent=None):

        """We need to provide tag_text explicitly, since it's possible that
        the cards have not yet been added to the database.

        """

        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.tag_text = tag_text
        self.cards = cards
        self.index = 0
        self.question.loadFinished.connect(self.question_load_finished)
        self.answer.loadFinished.connect(self.answer_load_finished)
        state = self.config()["preview_cards_dlg_state"]
        if state:
            self.restoreGeometry(state)
        self.update_dialog()

    def keyPressEvent(self, event):

        """When this dialog is called from the card browser, PageUp and
        PageDown keys can be used to move the previous/next card in the list.

        """
        
        if event.key() == QtCore.Qt.Key_PageUp:
            self.page_up_down_signal.emit(self.UP)
        elif event.key() == QtCore.Qt.Key_PageDown:
            self.page_up_down_signal.emit(self.DOWN)
        # Note QtGui.QWidget.keyPressEvent(self, event) does not seem to work,
        # so we handle the most common keypresses here too.
        if event.key() == QtCore.Qt.Key_Escape:
            self.reject()
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.accept()            
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def update_dialog(self):
        self.question_label.setText(_("Question: ") + self.tag_text)
        if len(self.cards) == 1:
            self.previous_button.setVisible(False)
            self.next_button.setVisible(False)
            self.fact_view_name.setVisible(False)            
        card = self.cards[self.index]
        self.question.setHtml(card.question())
        self.answer.setHtml(card.answer())
        self.fact_view_name.setText(_(card.fact_view.name) + " (" + \
            str(self.index + 1) + "/" + str(len(self.cards)) + ")")
        self.previous_button.setEnabled(self.index != 0)
        self.next_button.setEnabled(self.index != len(self.cards) - 1)

    def question_load_finished(self):
        stretch = determine_stretch_factor(self.question.page())
        self.vertical_layout.setStretchFactor(self.question_box, stretch)
        
    def answer_load_finished(self):
        stretch = determine_stretch_factor(self.answer.page())
        self.vertical_layout.setStretchFactor(self.answer_box, stretch)
        
    def previous(self):
        self.index -= 1
        self.update_dialog()

    def next(self):
        self.index += 1
        self.update_dialog()

    def _store_state(self):
        self.config()["preview_cards_dlg_state"] = self.saveGeometry()        

    def closeEvent(self, event):
        # Generated when clicking the window's close button.        
        self._store_state()        

    def accept(self):
        # 'accept' does not generate a close event.
        self._store_state()
        return QtGui.QDialog.accept(self)    
