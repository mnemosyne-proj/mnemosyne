#
# Widget to preview set of related cards <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_preview_cards_dlg import Ui_PreviewCardsDlg


class PreviewCardsDlg(QDialog, Ui_PreviewCardsDlg):

    def __init__(self, cards, cat_name_string, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.cards = cards
        self.index = 0
        self.question_label.setText(_("Question: ") + cat_name_string)
        self.update_dialog()

        #if cat != self.trUtf8("<default>"):
        #    self.question_label.setText(preprocess(\
        #        unicode(self.trUtf8("Question:")) + " " + cat))


        # TODO: obsolete?
        #if get_config("QA_font") != None:
        #    font = QFont()
        #    font.fromString(get_config("QA_font"))
        #    self.question.setFont(font)
        #    self.answer.setFont(font)
        #else:
        #    font = self.question_label.font()

        #if get_config("left_align") == True:
        #    alignment = Qt.AlignAuto    | Qt.AlignVCenter | Qt.WordBreak
        #else:
        #    alignment = Qt.AlignHCenter | Qt.AlignVCenter | Qt.WordBreak

        #self.question.setAlignment(alignment)
        #self.answer.setAlignment(alignment)


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
