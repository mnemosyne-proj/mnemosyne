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
            self.question_label.setText(escape("Question: " + cat))

        if get_config("QA_font") != None:
            font = QFont()
            font.fromString(get_config("QA_font"))
            self.question.setFont(font)
            self.answer.setFont(font)

        self.question.setText(escape(q))
        self.answer.setText(escape(a))
