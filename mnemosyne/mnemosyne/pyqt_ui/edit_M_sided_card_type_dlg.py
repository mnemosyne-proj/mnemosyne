# -*- coding: utf-8 -*-

#
# edit_M_sided_card_type_dlg.py <Peter.Bienstman@UGent.be>
#


from PyQt5 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.translator import _

from mnemosyne.pyqt_ui.ui_edit_M_side_card_type_dlg import \
     Ui_EditMSidedCardTypeDlg


class EditMSidedCardTypeDlg(QtWidgets.QDialog, Ui_EditMSidedCardTypeDlg):

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
        self.label1.setText(" →")
        self.label2.setText(" →")
        self.labelc1.setText(" ↗")
        self.labelc2.setText(" ↘")

        #if len(self.cards) > 1:
        #    tform.groupBox_3.setTitle(_(
        #        "Styling (shared between cards)"))
        self.front.textChanged.connect(self.update_preview)
        self.css.textChanged.connect(self.update_preview)
        self.back.textChanged.connect(self.update_preview)

        # preview area: preview.ui
        right = QtGui.QWidget()
        pform = aqt.forms.preview.Ui_Form()
        pform.setupUi(right)

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

