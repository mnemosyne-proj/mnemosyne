#
# browse_cards_dlg.py <Peter.Bienstman@UGent.be>
#

import sys
import time
import locale

from PyQt4 import QtCore, QtGui, QtSql

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import make_interval_string
from mnemosyne.pyqt_ui.ui_browse_cards_dlg import Ui_BrowseCardsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import BrowseCardsDialog

_ID = 0
ID = 1
CARD_TYPE_ID = 2
_FACT_ID = 3
_FACT_VIEW_ID = 4
QUESTION = 5
ANSWER = 6
TAGS = 7
GRADE = 8
NEXT_REP = 9
LAST_REP = 10
EASINESS = 11
ACQ_REPS = 12
RET_REPS = 13
LAPSES = 14
ACQ_REPS_SINCE_LAPSE = 15
RET_REPS_SINCE_LAPSE = 16
CREATION_TIME = 17
MODIFICATION_TIME = 18
EXTRA_DATA = 19
SCHEDULER_DATA = 20
ACTIVE = 21


class CardModel(QtSql.QSqlTableModel, Component):

    def __init__(self, component_manager):
        QtSql.QSqlTableModel.__init__(self)
        Component.__init__(self, component_manager)
        self.adjusted_now = self.scheduler().adjusted_now()
        self.date_format = locale.nl_langinfo(locale.D_FMT)
        self.background_colour_for_card_type_id = {}
        for card_type_id, rgb in \
            self.config()["background_colour"].iteritems():
            self.background_colour_for_card_type_id[card_type_id] = \
                QtGui.QColor(rgb)    
        self.font_colour_for_card_type_id = {}
        for card_type_id in self.config()["font_colour"]:
            first_key = self.card_type_by_id(card_type_id).fields[0][0]
            self.font_colour_for_card_type_id[card_type_id] = QtGui.QColor(\
                self.config()["font_colour"][card_type_id][first_key])
        
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.TextColorRole: 
            card_type_id_index = self.index(index.row(), CARD_TYPE_ID)
            card_type_id = str(QtSql.QSqlTableModel.data(\
                self, card_type_id_index).toString())
            colour = QtGui.QColor(QtCore.Qt.black)
            if card_type_id in self.font_colour_for_card_type_id:
                colour = self.font_colour_for_card_type_id[card_type_id]
            return QtCore.QVariant(colour)
        if role == QtCore.Qt.BackgroundColorRole:
            card_type_id_index = self.index(index.row(), CARD_TYPE_ID)
            card_type_id = str(QtSql.QSqlTableModel.data(\
                self, card_type_id_index).toString())
            if card_type_id in self.background_colour_for_card_type_id:
                return QtCore.QVariant(\
                    self.background_colour_for_card_type_id[card_type_id])
            else:
                return QtCore.QVariant(QtGui.QFont("white"))
        column = index.column()
        if role == QtCore.Qt.TextAlignmentRole and column not in \
            (QUESTION, ANSWER, TAGS):
            return QtCore.QVariant(QtCore.Qt.AlignCenter)
        if role == QtCore.Qt.FontRole and column not in \
            (QUESTION, ANSWER, TAGS):
            active_index = self.index(index.row(), ACTIVE)
            active = QtSql.QSqlTableModel.data(self, active_index).toInt()[0]
            font = QtGui.QFont()
            if not active:
                font.setStrikeOut(True)
            return QtCore.QVariant(font)
        if role != QtCore.Qt.DisplayRole:
            return QtSql.QSqlTableModel.data(self, index, role)
        # Display roles to format some columns in a more pretty way. Note that
        # sorting still uses the orginal database fields, which is good
        # for speed.
        if column == GRADE:
            grade = QtSql.QSqlTableModel.data(self, index).toInt()[0]
            if grade == -1:
                return QtCore.QVariant(_("Yet to learn"))
            else:
                return QtCore.QVariant(grade)
        if column == NEXT_REP:
            next_rep = QtSql.QSqlTableModel.data(self, index, role).toInt()[0]
            if next_rep == -1:
                return QtCore.QVariant("")
            return QtCore.QVariant(\
                self.scheduler().next_rep_to_interval_string(next_rep))
        if column == LAST_REP:
            last_rep = QtSql.QSqlTableModel.data(self, index, role).toInt()[0]
            if last_rep == -1:
                return QtCore.QVariant("")
            return QtCore.QVariant(\
                self.scheduler().last_rep_to_interval_string(last_rep))
        if column == EASINESS:
            old_data = QtSql.QSqlTableModel.data(self, index, role).toString()
            return QtCore.QVariant("%.2f" % float(old_data))
        if column in (CREATION_TIME, MODIFICATION_TIME):    
            old_data = QtSql.QSqlTableModel.data(self, index, role).toInt()[0]
            return QtCore.QVariant(time.strftime(self.date_format,
                time.gmtime(old_data)))
        return QtSql.QSqlTableModel.data(self, index, role)

 
class QA_Delegate(QtGui.QStyledItemDelegate, Component):

    # http://stackoverflow.com/questions/1956542/
    # how-to-make-item-view-render-rich-html-text-in-qt

    def __init__(self, component_manager, Q_or_A, parent=None):
        Component.__init__(self, component_manager)
        QtGui.QItemDelegate.__init__(self, parent)
        self.doc = QtGui.QTextDocument(self)
        self.Q_or_A = Q_or_A

    def paint(self, painter, option, index):
        optionV4 = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(optionV4, index)
        if optionV4.widget:
            style = optionV4.widget.style()
        else:
            style = QtGui.QApplication.style()
        # Get the data.
        _id_index = index.model().index(index.row(), _ID)
        _id = index.model().data(_id_index).toInt()[0]
        ignore_text_colour = bool(optionV4.state & QtGui.QStyle.State_Selected)
        card = self.component_manager.current("database").\
            card(_id, id_is_internal=True)
        if self.Q_or_A == QUESTION:
            self.doc.setHtml(card.question(render_chain="card_browser",
                ignore_text_colour=ignore_text_colour))
        else:
            self.doc.setHtml(card.answer(render_chain="card_browser",
                ignore_text_colour=ignore_text_colour))
        # Paint the item without the text.
        optionV4.text = QtCore.QString()
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, optionV4, painter)
        context = QtGui.QAbstractTextDocumentLayout.PaintContext() 
        # Highlight text if item is selected.
        if optionV4.state & QtGui.QStyle.State_Selected:
            context.palette.setColor(QtGui.QPalette.Text,
                optionV4.palette.color(QtGui.QPalette.Active,
                                       QtGui.QPalette.HighlightedText))
        rect = \
             style.subElementRect(QtGui.QStyle.SE_ItemViewItemText, optionV4)
        painter.save()

        # No longer used (done in model for all columns),
        # but kept for reference.
        #if not (optionV4.state & QtGui.QStyle.State_Selected) and \
        #    not (optionV4.state & QtGui.QStyle.State_MouseOver):
        #     painter.fillRect(rect, QtGui.QColor("red"))

        painter.translate(rect.topLeft())
        painter.translate(0, 3)  # There seems to be a small offset needed...
        painter.setClipRect(rect.translated(-rect.topLeft()))
        self.doc.documentLayout().draw(painter, context)
        painter.restore()

        
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
        self.card_model = CardModel(component_manager)
        self.card_model.setTable("cards")
        headers = {QUESTION: _("Question"), ANSWER: _("Answer"),
            TAGS: _("Tags"), GRADE: _("Grade"), NEXT_REP: _("Next rep"),
            LAST_REP: _("Last rep"), EASINESS: _("Easiness"),
            ACQ_REPS: _("Acquisition\nreps"),
            RET_REPS: _("Retention\nreps"), LAPSES: _("Lapses"),
            CREATION_TIME: _("Created"), MODIFICATION_TIME: _("Modified")}
        for key, value in headers.iteritems():
              self.card_model.setHeaderData(key, QtCore.Qt.Horizontal,
                  QtCore.QVariant(value))
        self.card_model.select()
        self.table.setModel(self.card_model)
        self.table.setItemDelegateForColumn(\
            QUESTION, QA_Delegate(component_manager, QUESTION, self))
        self.table.setItemDelegateForColumn(\
            ANSWER, QA_Delegate(component_manager, ANSWER, self))
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().hide()
        for column in (_ID, ID, CARD_TYPE_ID, _FACT_ID, _FACT_VIEW_ID,
            ACQ_REPS_SINCE_LAPSE, RET_REPS_SINCE_LAPSE,
            EXTRA_DATA, ACTIVE, SCHEDULER_DATA):
            self.table.setColumnHidden(column, True)        
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

