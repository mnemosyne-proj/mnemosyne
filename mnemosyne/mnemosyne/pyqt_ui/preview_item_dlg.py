##############################################################################
#
# Widget to preview single item <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from mnemosyne.core import *
from preview_item_frm import *
from sound import *

    
##############################################################################
#
# PreviewItemDlg
#
##############################################################################

class PreviewItemDlg(PreviewItemFrm):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self, q, a, cat, parent=None, name=None, modal=0, fl=0):

        PreviewItemFrm.__init__(self,parent,name,modal,fl)

        if cat != self.trUtf8("<default>"):
            self.question_label.setText(preprocess(\
                unicode(self.trUtf8("Question:")) + " " + cat))

        if get_config("QA_font") != None:
            font = QFont()
            font.fromString(get_config("QA_font"))
            self.question.setFont(font)
            self.answer.setFont(font)
        else:
            font = self.question_label.font()

        if get_config("left_align") == True:
            alignment = Qt.AlignAuto    | Qt.AlignVCenter | Qt.WordBreak
        else:
            alignment = Qt.AlignHCenter | Qt.AlignVCenter | Qt.WordBreak

        self.question.setAlignment(alignment)
        self.answer.setAlignment(alignment)

        # Question and answer fields.

        increase_non_latin = get_config("non_latin_font_size_increase")
        non_latin_size = font.pointSize() + increase_non_latin

        text = preprocess(q)
        play_sound(text)
        if increase_non_latin:
            text = set_non_latin_font_size(text, non_latin_size)
        self.question.setText(text)

        text = preprocess(a)
        play_sound(text)
        if increase_non_latin:
            text = set_non_latin_font_size(text, non_latin_size)
        self.answer.setText(text)        
