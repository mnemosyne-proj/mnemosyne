#
# browse_cards_dlg.py <Peter.Bienstman@UGent.be>
#

import sys
import time
import locale

from PyQt4 import QtCore, QtGui, QtSql

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.tag_tree_wdgt import TagsTreeWdgt
from mnemosyne.pyqt_ui.convert_card_type_fields_dlg import \
     ConvertCardTypeFieldsDlg
from mnemosyne.pyqt_ui.ui_browse_cards_dlg import Ui_BrowseCardsDlg
from mnemosyne.pyqt_ui.card_type_tree_wdgt import CardTypesTreeWdgt
from mnemosyne.libmnemosyne.ui_components.dialogs import BrowseCardsDialog
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion


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
        self.search_string = ""
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
        QtGui.QStyledItemDelegate.__init__(self, parent)
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
        search_string = index.model().search_string
        card = self.component_manager.current("database").\
            card(_id, id_is_internal=True)
        if self.Q_or_A == QUESTION:
            self.doc.setHtml(card.question(render_chain="card_browser",
                ignore_text_colour=ignore_text_colour,
                search_string=search_string))
        else:
            self.doc.setHtml(card.answer(render_chain="card_browser",
                ignore_text_colour=ignore_text_colour,
                search_string=search_string))
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
        self.saved_index = None
        # Set up card type tree.
        self.container_1 = QtGui.QWidget(self.splitter_1)
        self.layout_1 = QtGui.QVBoxLayout(self.container_1)
        self.label_1 = QtGui.QLabel(_("Show cards from these card types:"),
            self.container_1)
        self.layout_1.addWidget(self.label_1)
        self.card_type_tree_wdgt = \
            CardTypesTreeWdgt(component_manager, self.container_1)
        self.layout_1.addWidget(self.card_type_tree_wdgt)
        self.splitter_1.insertWidget(0, self.container_1)
        # Set up tag tree plus search box.
        self.container_2 = QtGui.QWidget(self.splitter_1)
        self.layout_2 = QtGui.QVBoxLayout(self.container_2)
        self.label_2 = QtGui.QLabel(_("having any of these tags:"),
            self.container_2)
        self.layout_2.addWidget(self.label_2)
        self.tag_tree_wdgt = \
            TagsTreeWdgt(component_manager, self.container_2,
                 self.unload_qt_database, self.display_card_table)
        self.layout_2.addWidget(self.tag_tree_wdgt)
        self.label_3 = QtGui.QLabel(_("containing this text:"),
            self.container_2)
        self.layout_2.addWidget(self.label_3)
        self.search_box = QtGui.QLineEdit(self.container_2)
        self.search_box.textChanged.connect(self.update_filter)
        self.search_box.setFocus()
        self.layout_2.addWidget(self.search_box)
        self.splitter_1.insertWidget(1, self.container_2)
        # Fill tree widgets.
        self.card_type_tree_wdgt.display()
        self.tag_tree_wdgt.display()
        self.display_card_table()
        self.card_type_tree_wdgt.card_type_tree.\
            itemClicked.connect(self.update_filter)
        self.tag_tree_wdgt.tag_tree_wdgt.\
            itemClicked.connect(self.update_filter)
        # Context menu.
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.context_menu)
        # Restore settings.
        width, height = self.config()["browse_cards_dlg_size"]
        if width:
            self.resize(width, height)
        splitter_1_sizes = self.config()["browse_cards_dlg_splitter_1"]
        if not splitter_1_sizes:
            self.splitter_1.setSizes([230, 320])
        else:
            self.splitter_1.setSizes(splitter_1_sizes)
        splitter_2_sizes = self.config()["browse_cards_dlg_splitter_2"]
        if not splitter_2_sizes:
            self.splitter_2.setSizes([333, 630])
        else:
            self.splitter_2.setSizes(splitter_2_sizes)

    def context_menu(self, point):
        menu = QtGui.QMenu(self)
        edit_action = QtGui.QAction(_("&Edit"), menu)
        edit_action.setShortcut(QtCore.Qt.Key_Enter)
        edit_action.triggered.connect(self.menu_edit)
        menu.addAction(edit_action)
        preview_action = QtGui.QAction(_("&Preview"), menu)
        preview_action.triggered.connect(self.menu_preview)
        menu.addAction(preview_action)
        delete_action = QtGui.QAction(_("&Delete"), menu)
        delete_action.setShortcut(QtGui.QKeySequence.Delete)
        delete_action.triggered.connect(self.menu_delete)
        menu.addAction(delete_action)
        menu.addSeparator()
        change_card_type_action = QtGui.QAction(_("Change card &type"), menu)
        change_card_type_action.triggered.connect(self.menu_change_card_type)
        menu.addAction(change_card_type_action)
        menu.addSeparator()
        add_tag_action = QtGui.QAction(_("&Add tag"), menu)
        add_tag_action.triggered.connect(self.menu_add_tag)
        menu.addAction(add_tag_action)
        remove_tag_action = QtGui.QAction(_("&Remove tag"), menu)
        remove_tag_action.triggered.connect(self.menu_remove_tag)
        menu.addAction(remove_tag_action)
        indexes = self.table.selectionModel().selectedRows()
        if len(indexes) > 1:
            edit_action.setEnabled(False)
            preview_action.setEnabled(False)            
        if len(indexes) >= 1:
            menu.exec_(self.table.mapToGlobal(point))
            
    def keyPressEvent(self, event):
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.menu_edit()
        elif event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            self.menu_delete()

    def cards_from_single_selection(self):
        index = self.table.selectionModel().selectedRows()[0]
        _fact_id_index = index.model().index(\
            index.row(), _FACT_ID, index.parent())
        _fact_id = index.model().data(_fact_id_index).toInt()[0]
        fact = self.database().fact(_fact_id, id_is_internal=True)
        return self.database().cards_from_fact(fact)

    def facts_from_selection(self):
        _fact_ids = set()
        for index in self.table.selectionModel().selectedRows():
            _fact_id_index = index.model().index(\
                index.row(), _FACT_ID, index.parent())
            _fact_id = index.model().data(_fact_id_index).toInt()[0]
            _fact_ids.add(_fact_id)
        facts = []
        for _fact_id in _fact_ids:
            facts.append(self.database().fact(_fact_id, id_is_internal=True))
        return facts
            
    def menu_edit(self):
        cards = self.cards_from_single_selection()
        dlg = self.component_manager.current("edit_card_dialog")\
            (cards[0], self.component_manager)
        dlg.before_apply_hook = self.unload_qt_database
        if dlg.exec_() == QtGui.QDialog.Accepted:
            self.display_card_table()
            self.card_type_tree_wdgt.rebuild()
            self.tag_tree_wdgt.rebuild()
                    
    def menu_preview(self):
        from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
        cards = self.cards_from_single_selection()
        tag_text = cards[0].tag_string()
        dlg = PreviewCardsDlg(cards, tag_text, self)
        dlg.exec_()

    def menu_delete(self):
        answer = self.main_widget().show_question\
            (_("Go ahead with delete? Sister cards will be deleted as well."),
            _("&OK"), _("&Cancel"), "")
        if answer == 1: # Cancel.
            return
        facts = []
        for index in self.table.selectionModel().selectedRows():
            _fact_id_index = index.model().index(\
                index.row(), _FACT_ID, index.parent())
            _fact_id = index.model().data(_fact_id_index).toInt()[0]
            facts.append(self.database().fact(_fact_id, id_is_internal=True))
        self.unload_qt_database()
        self.saved_selection = []
        self.controller().delete_facts_and_their_cards(facts)        
        self.display_card_table()
        self.card_type_tree_wdgt.rebuild()
        self.tag_tree_wdgt.rebuild()

    def menu_change_card_type(self):
        # Test if all selected cards have the same card type.
        current_card_type_ids = set()
        for index in self.table.selectionModel().selectedRows():
            card_type_id_index = index.model().index(\
                index.row(), CARD_TYPE_ID, index.parent())
            card_type_id = \
                unicode(index.model().data(card_type_id_index).toString()[0])
            current_card_type_ids.add(card_type_id)
            if len(current_card_type_ids) > 1:
                self.main_widget().show_error\
                    (_("The selected cards should have the same card type."))
                return
        current_card_type = self.card_type_by_id(current_card_type_ids.pop())
        # Get new card type. Use a dict as backdoor to return values
        # from the dialog.
        return_values = {}
        from mnemosyne.pyqt_ui.change_card_type_dlg import ChangeCardTypeDlg
        dlg = ChangeCardTypeDlg(self.component_manager,
            current_card_type, return_values)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return
        print return_values['new_card_type'].name
        return
    

        # Get correspondence.
        self.correspondence = {}

        #if not self.card_type.keys().issubset(new_card_type.keys()):      
        #dlg = ConvertCardTypeFieldsDlg(self.card_type, new_card_type,
        #                               self.correspondence, self)
        #if dlg.exec_() == 0:  # Reject. TODO; use proper return values, also in edit.
        #    self.card_types_widget.setCurrentIndex(self.card_type_index)
        #    return
        #else:          
        #    self.update_card_widget()

        # Start the actual conversion.
        facts = self.facts_from_selection()
        self.unload_qt_database()
        self.controller().change_card_type(self, facts, new_card_type,
            self.correspondence)
        self.display_card_table()
        self.card_type_tree_wdgt.rebuild()
        
    def menu_add_tag(self):
        print 'add tag'
        self.unload_qt_database()

        self.display_card_table()
        self.tag_tree_wdgt.rebuild()
        
    def menu_remove_tag(self):
        print 'remove_tag'
        self.unload_qt_database()

        self.display_card_table()
        self.tag_tree_wdgt.rebuild()
        
    def load_qt_database(self):
        self.database().release_connection()
        qt_db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        qt_db.setDatabaseName(self.database().path())
        if not qt_db.open():
            QtGui.QMessageBox.warning(None, _("Mnemosyne"),
                _("Database error: ") + qt_db.lastError().text())
            sys.exit(1)

    def unload_qt_database(self):
        self.saved_index = self.table.indexAt(QtCore.QPoint(0,0))
        self.saved_selection = self.table.selectionModel().selectedRows()
        self.config()["browse_cards_dlg_table_settings"] \
            = self.table.horizontalHeader().saveState()
        self.table.setModel(QtGui.QStandardItemModel())
        del self.card_model
        QtSql.QSqlDatabase.removeDatabase(\
            QtSql.QSqlDatabase.database().connectionName())

    def display_card_table(self):
        self.load_qt_database()
        self.card_model = CardModel(self.component_manager)
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
        self.table.setModel(self.card_model)
        table_settings = self.config()["browse_cards_dlg_table_settings"]
        if table_settings:
            self.table.horizontalHeader().restoreState(table_settings)
        self.table.setItemDelegateForColumn(\
            QUESTION, QA_Delegate(self.component_manager, QUESTION, self))
        self.table.setItemDelegateForColumn(\
            ANSWER, QA_Delegate(self.component_manager, ANSWER, self))
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.menu_edit)
        self.table.verticalHeader().hide()
        for column in (_ID, ID, CARD_TYPE_ID, _FACT_ID, _FACT_VIEW_ID,
            ACQ_REPS_SINCE_LAPSE, RET_REPS_SINCE_LAPSE,
            EXTRA_DATA, ACTIVE, SCHEDULER_DATA):
            self.table.setColumnHidden(column, True)
        query = QtSql.QSqlQuery("select count() from tags")
        query.first()
        self.tag_count = query.value(0).toInt()[0]
        self.update_filter() # Needed after tag rename.
        self.update_card_counters()
        self.card_model.select()
        if self.saved_index:
            # All of the statements below are needed.
            # Qt does not (yet) seem to allow to restore the previous column
            # correctly.
            self.saved_index = self.card_model.index(self.saved_index.row(),
                self.saved_index.column())
            self.table.scrollTo(self.saved_index)
            self.table.scrollTo(self.saved_index,
                QtGui.QAbstractItemView.PositionAtTop)
            # Restore selection.
            old_selection_mode = self.table.selectionMode()
            self.table.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
            for index in self.saved_selection:
                self.table.selectRow(index.row())
            self.table.setSelectionMode(old_selection_mode)
            
    def activate(self):
        self.exec_()

    def update_filter(self):
        # Card types and fact views.
        criterion = DefaultCriterion(self.component_manager)
        self.card_type_tree_wdgt.checked_to_criterion(criterion)
        filter = ""
        for card_type_id, fact_view_id in \
                criterion.deactivated_card_type_fact_view_ids:
            filter += """not (cards.fact_view_id='%s' and
                cards.card_type_id='%s') and """ \
                % (fact_view_id, card_type_id)
        filter = filter.rsplit("and ", 1)[0]
        # Tags.
        self.tag_tree_wdgt.checked_to_active_tags_in_criterion(criterion)
        if len(criterion.active_tag__ids) == 0:
            filter = "_id='not_there'"
        elif len(criterion.active_tag__ids) != self.tag_count:
            if filter:
                filter += "and "
            filter += "_id in (select _card_id from tags_for_card where "
            for _tag_id in criterion.active_tag__ids:
                filter += "_tag_id='%s' or " % (_tag_id, )
            filter = filter.rsplit("or ", 1)[0] + ")"
        # Search string.
        search_string = unicode(self.search_box.text())
        self.card_model.search_string = search_string
        if search_string:
            if filter:
                filter += "and "
            filter += "(question like '%%%s%%' or answer like '%%%s%%')" \
                % (search_string, search_string)
        self.card_model.setFilter(filter)
        self.card_model.select()
        self.update_card_counters()

    def update_card_counters(self):
        filter = self.card_model.filter()
        # Selected count.
        query_string = "select count() from cards"
        if filter:
            query_string += " where " + filter
        query = QtSql.QSqlQuery(query_string)
        query.first()
        selected = query.value(0).toInt()[0]
        # Active selected count.
        if not filter:
            query_string += " where active=1"
        else:
            query_string += " and active=1"
        query = QtSql.QSqlQuery(query_string)
        query.first()
        active = query.value(0).toInt()[0]
        self.counter_label.setText(\
            "%d cards selected, of which %d are active" % (selected, active))   
        
    def closeEvent(self, event):
        self.unload_qt_database()                
        self.config()["browse_cards_dlg_size"] = (self.width(), self.height())
        self.config()["browse_cards_dlg_splitter_1"] \
            = self.splitter_1.sizes()
        self.config()["browse_cards_dlg_splitter_2"] \
           = self.splitter_2.sizes()        
        self.config()["browse_cards_dlg_table_settings"] \
            = self.table.horizontalHeader().saveState()
