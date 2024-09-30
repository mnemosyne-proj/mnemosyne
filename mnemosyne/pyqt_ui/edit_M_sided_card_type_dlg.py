#
# edit_M_sided_card_type_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_edit_M_sided_card_type_dlg import \
     Ui_EditMSidedCardTypeDlg
from mnemosyne.pyqt_ui.edit_M_sided_card_template_wdgt import \
     EditMSidedCardTemplateWdgt
from mnemosyne.libmnemosyne.ui_components.dialogs import \
     EditMSidedCardTypeDialog


class EditMSidedCardTypeDlg(QtWidgets.QDialog, EditMSidedCardTypeDialog,
                            Ui_EditMSidedCardTypeDlg):

    def __init__(self, card_type, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        self.card_type = card_type
        for fact_view in self.card_type.fact_views:
            widget = EditMSidedCardTemplateWdgt(card_type, fact_view,
                component_manager=self.component_manager, parent=self)
            self.tab_widget.addTab(widget, _(fact_view.name))
        self.tab_widget.tabBar().setVisible(self.tab_widget.count() > 1)
        self.ok_button.setFocus()
        state = self.config()["edit_M_sided_card_type_dlg_state"]
        if state:
            self.restoreGeometry(state)

    def activate(self):
        EditMSidedCardTypeDialog.activate(self)
        self.exec()

    def _store_state(self):
        self.config()["edit_M_sided_card_type_dlg_state"] = self.saveGeometry()

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()

    def accept(self):
        for index in range(self.tab_widget.count()):
            ok = self.tab_widget.widget(index).apply()
            if not ok:
                return
        self._store_state()
        return QtWidgets.QDialog.accept(self)

    def reject(self):
        self._store_state()
        for index in range(self.tab_widget.count()):
            if hasattr(self.tab_widget.widget(index), "reject"):
                self.tab_widget.widget(index).reject()
        return QtWidgets.QDialog.reject(self)

