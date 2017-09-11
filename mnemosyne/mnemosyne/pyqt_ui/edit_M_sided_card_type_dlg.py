# -*- coding: utf-8 -*-

#
# edit_M_sided_card_type_dlg.py <Peter.Bienstman@UGent.be>
#


from PyQt5 import QtCore, QtGui, QtWidgets

# TODO: check
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.card_type import CardType
from mnemosyne.pyqt_ui.clone_card_type_dlg import CloneCardTypeDlg
from mnemosyne.pyqt_ui.ui_manage_card_types_dlg import Ui_ManageCardTypesDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import ManageCardTypesDialog


class ManageCardTypesDlg(QtWidgets.QDialog, ManageCardTypesDialog,
                         Ui_ManageCardTypesDlg):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        w = QtGui.QWidget()
        l = QtWidgets.QHBoxLayout()
        l.setContentsMargins(0,0,0,0)
        l.setSpacing(3)
        left = QtGui.QWidget()
        # template area ("template.ui")
        tform = aqt.forms.template.Ui_Form()
        tform.setupUi(left)
        tform.label1.setText(" →")
        tform.label2.setText(" →")
        tform.labelc1.setText(" ↗")
        tform.labelc2.setText(" ↘")
        if self.style().objectName() == "gtk+":
            # gtk+ requires margins in inner layout
            tform.tlayout1.setContentsMargins(0, 11, 0, 0)
            tform.tlayout2.setContentsMargins(0, 11, 0, 0)
            tform.tlayout3.setContentsMargins(0, 11, 0, 0)
        if len(self.cards) > 1:
            tform.groupBox_3.setTitle(_(
                "Styling (shared between cards)"))
        tform.front.textChanged.connect(self.saveCard)
        tform.css.textChanged.connect(self.saveCard)
        tform.back.textChanged.connect(self.saveCard)
        l.addWidget(left, 5)
        # preview area: preview.ui
        right = QtGui.QWidget()
        pform = aqt.forms.preview.Ui_Form()
        pform.setupUi(right)
        if self.style().objectName() == "gtk+":
            # gtk+ requires margins in inner layout
            pform.frontPrevBox.setContentsMargins(0, 11, 0, 0)
            pform.backPrevBox.setContentsMargins(0, 11, 0, 0)
        # for cloze notes, show that it's one of n cards
        if self.model['type'] == MODEL_CLOZE:
            cnt = len(self.mm.availOrds(
                self.model, joinFields(self.note.fields)))
            for g in pform.groupBox, pform.groupBox_2:
                g.setTitle(g.title() + _(" (1 of %d)") % max(cnt, 1))
        pform.frontWeb = AnkiWebView()
        pform.frontPrevBox.addWidget(pform.frontWeb)
        pform.backWeb = AnkiWebView()
        pform.backPrevBox.addWidget(pform.backWeb)
        l.addWidget(right, 5)
        w.setLayout(l)
        self.forms.append({'tform': tform, 'pform': pform})
        self.tabs.addTab(w, t['name'])
        self.exec_()

