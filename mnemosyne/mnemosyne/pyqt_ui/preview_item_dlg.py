##############################################################################
#
# Widget to preview single item <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *
from mnemosyne.core import *
from preview_item_frm import *

    
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

        if cat != "<default>":
            self.question_label.setText(preprocess("Question: " + cat))

        if get_config("QA_font") != None:
            font = QFont()
            font.fromString(get_config("QA_font"))
            self.question.setFont(font)
            self.answer.setFont(font)

        if get_config("left_align") == True:
            alignment = Qt.AlignAuto | Qt.AlignVCenter
        else:
            alignment = Qt.AlignCenter

        self.question.setAlignment(alignment)
        self.answer.setAlignment(alignment)

        self.question.setText(preprocess(q))
        self.answer.setText(preprocess(a))
