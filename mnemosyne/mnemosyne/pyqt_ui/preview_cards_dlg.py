#
# Widget to preview set of sister cards <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_preview_cards_dlg import Ui_PreviewCardsDlg

class PreviewCardsDlg(QtGui.QDialog, Ui_PreviewCardsDlg, Component):

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
        self.cards = cards
        self.index = 0
        self.question_label.setText(_("Question: ") + tag_text)
        state = self.config()["preview_cards_dlg_state"]
        if state:
            self.restoreGeometry(state)
        self.update_dialog()

    def activate(self):
        self.retranslateUi(self)

    def update_dialog(self):
        if len(self.cards) == 1:
            self.previous_button.setVisible(False)
            self.next_button.setVisible(False)
            self.fact_view_name.setVisible(False)            
        card = self.cards[self.index]
        q_stretch, a_stretch = \
            self.review_widget().determine_stretch_factors(\
            card.question("plain_text"), card.answer("plain_text"))
        self.vertical_layout.setStretchFactor(self.question_box, q_stretch)
        self.vertical_layout.setStretchFactor(self.answer_box, a_stretch)
        self.question.setHtml(card.question())
        self.answer.setHtml(card.answer())
        self.fact_view_name.setText(card.fact_view.name + " (" + \
                        str(self.index+1) + "/" + str(len(self.cards)) + ")")
        self.previous_button.setEnabled(self.index != 0)
        self.next_button.setEnabled(self.index != len(self.cards)-1)

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
