#
# edit_M_sided_card_template_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtWidgets

from mnemosyne.pyqt_ui.ui_edit_M_sided_card_template_wdgt import \
     Ui_EditMSidedCardTemplateWdgt
from mnemosyne.libmnemosyne.ui_components.dialogs import \
     EditMSidedCardTemplateWidget

class EditMSidedCardTemplateWdgt(QtWidgets.QDialog,
                                 EditMSidedCardTemplateWidget,
                                 Ui_EditMSidedCardTemplateWdgt):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)

        # TODO: move to designer?
        self.front_template.textChanged.connect(self.update_preview)
        self.css.textChanged.connect(self.update_preview)
        self.back_template.textChanged.connect(self.update_preview)

    def update_preview(self):
        pass

    def apply(self):
        pass

