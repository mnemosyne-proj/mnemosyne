#
# browse_cards_dlg.py <Peter.Bienstman@UGent.be>
#

import sys
import time
import locale
from PyQt4 import QtCore, QtGui, QtSql

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.pyqt_ui.ui_browse_cards_dlg import Ui_BrowseCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import BrowseCardsDialog

_ID = 0
ID = 1
_FACT_ID = 2
_FACT_VIEW_ID = 3
QUESTION = 4
ANSWER = 5
GRADE = 6
NEXT_REP = 7
LAST_REP = 8
EASINESS = 9
ACQ_REPS = 10
RET_REPS = 11
LAPSES = 12
ACQ_REPS_SINCE_LAPSE = 13
RET_REPS_SINCE_LAPSE = 14
EXTRA_DATA = 15
SCHEDULER_DATA = 16
ACTIVE = 17

class CardModel(QtSql.QSqlTableModel):

    def __init__(self, parent=None):
        QtSql.QSqlTableModel.__init__(self)
        self.date_format = locale.nl_langinfo(locale.D_FMT)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and index.column() == EASINESS:
            old_data = QtSql.QSqlTableModel.data(self, index, role).toString()
            return QtCore.QVariant("%.2f" % float(old_data))
        if role == QtCore.Qt.DisplayRole and \
            (index.column() == NEXT_REP or index.column() == LAST_REP):
            old_data = QtSql.QSqlTableModel.data(self, index, role).toInt()[0]
            return QtCore.QVariant(time.strftime(self.date_format,
                time.gmtime(old_data)))
        if role == QtCore.Qt.TextAlignmentRole and \
            index.column() != QUESTION and index.column() != ANSWER:
            return QtCore.QVariant(QtCore.Qt.AlignCenter)  
        
        return QtSql.QSqlTableModel.data(self, index, role)


class BrowseCardsDlg(QtGui.QDialog, Ui_BrowseCardsDlg, BrowseCardsDialog):

    def __init__(self, component_manager):
        BrowseCardsDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)

        self.database().release_connection()

        self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.database().path())
        if not self.db.open():
            QtGui.QMessageBox.warning(None, _("Mnemosyne"),
                _("Database error: ") + self.db.lastError().text())
            sys.exit(1)

        self.card_model = CardModel(self)
        
        self.card_model.setTable("cards")
        #self.card_model.setRelation(CATEGORYID,
        #        QSqlRelation("categories", "id", "name"))
        #self.card_model.setSort(GRADE, QtCore.Qt.AscendingOrder)

        headers = {QUESTION: _("Question"), ANSWER: _("Answer"),
            GRADE: _("Grade"), NEXT_REP: _("Next rep"),
            LAST_REP: _("Last rep"), EASINESS: _("Easiness"),
            ACQ_REPS: _("Acquisition\nreps"),
            RET_REPS: _("Retention\nreps"), LAPSES: _("Lapses")}
        for key, value in headers.iteritems():
              self.card_model.setHeaderData(key, QtCore.Qt.Horizontal,
                  QtCore.QVariant(value))

        self.card_model.select()

        self.table.setModel(self.card_model)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.setColumnHidden(_ID, True)
        self.table.setColumnHidden(ID, True)
        self.table.setColumnHidden(_FACT_ID, True)
        self.table.setColumnHidden(_FACT_VIEW_ID, True)
        self.table.setColumnHidden(ACQ_REPS_SINCE_LAPSE, True)
        self.table.setColumnHidden(RET_REPS_SINCE_LAPSE, True)
        self.table.setColumnHidden(EXTRA_DATA, True)
        self.table.setColumnHidden(ACTIVE, True)
        self.table.setColumnHidden(SCHEDULER_DATA, True)
    
        #self.table.resizeColumnsToContents()
        
        width, height = self.config()["browse_dlg_size"]
        if width:
            self.resize(width, height)
        
    def activate(self):
        self.exec_()
        
    def closeEvent(self, event):
        self.db.close()
        self.config()["browse_dlg_size"] = (self.width(), self.height())
        
    def accept(self):
        self.db.close()
        self.config()["browse_dlg_size"] = (self.width(), self.height())
        return QtGui.QDialog.accept(self)       

