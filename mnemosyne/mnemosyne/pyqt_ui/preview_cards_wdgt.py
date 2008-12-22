#
# Widget to preview set of related cards <Peter.Bienstman@UGent.be>
#

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_preview_cards_wdgt import Ui_PreviewCardsWdgt


class PreviewCardsWdgt(QDialog, Ui_PreviewCardsWdgt):

    def __init__(self, filename, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

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

