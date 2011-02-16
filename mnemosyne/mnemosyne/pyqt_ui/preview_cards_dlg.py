#
# Widget to preview set of sister cards <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_preview_cards_dlg import Ui_PreviewCardsDlg


class PreviewCardsDlg(QtGui.QDialog, Ui_PreviewCardsDlg):

    def __init__(self, cards, tag_text, parent=None):

        """We need to provide tag_text explicitly, since it's possible that
        the cards have not yet been added to the database.

        """
        
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cards = cards
        self.index = 0
        self.question_label.setText(_("Question: ") + tag_text)
        self.update_dialog()

    def update_dialog(self):
        if len(self.cards) == 1:
            self.previous_button.setVisible(False)
            self.next_button.setVisible(False)
            self.fact_view_name.setVisible(False)            
        card = self.cards[self.index]
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