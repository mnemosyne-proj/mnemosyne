#
# edit_M_sided_card_template_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore

from mnemosyne.pyqt_ui.ui_edit_M_sided_card_template_wdgt import \
     Ui_EditMSidedCardTemplateWdgt


class EditMSidedCardTypeDlg(QtWidgets.QDialog, Ui_EditMSidedCardTemplateWdgt):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)

        self.front_template.textChanged.connect(self.update_preview)
        self.css.textChanged.connect(self.update_preview)
        self.back_template.textChanged.connect(self.update_preview)

    def update_preview(self):
        pass

