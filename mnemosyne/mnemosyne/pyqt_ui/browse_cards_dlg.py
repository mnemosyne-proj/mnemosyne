#
# browse_cards_dlg.py <Peter.Bienstman@UGent.be>
#

import sys
import time
import locale

from PyQt4 import QtCore, QtGui, QtSql

from mnemosyne.libmnemosyne.tag import Tag
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.card import Card
from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.tag_tree_wdgt import TagsTreeWdgt
from mnemosyne.pyqt_ui.ui_browse_cards_dlg import Ui_BrowseCardsDlg
from mnemosyne.pyqt_ui.card_type_tree_wdgt import CardTypesTreeWdgt
from mnemosyne.libmnemosyne.ui_components.dialogs import BrowseCardsDialog
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion
from mnemosyne.pyqt_ui.convert_card_type_keys_dlg import \
     ConvertCardTypeKeysDlg
from mnemosyne.pyqt_ui.tip_after_starting_n_times import \
     TipAfterStartingNTimes

_ID = 0
ID = 1
CARD_TYPE_ID = 2
_FACT_ID = 3
FACT_VIEW_ID = 4
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
        try:
            self.date_format = locale.nl_langinfo(locale.D_FMT)
        except:
            self.date_format = "%m/%d/%y"
        self.background_colour_for_card_type_id = {}
        for card_type_id, rgb in \
            self.config()["background_colour"].iteritems():
            # If the card type has been deleted since, don't bother.
            if not card_type_id in self.component_manager.card_type_with_id:
                continue
            self.background_colour_for_card_type_id[card_type_id] = \
                QtGui.QColor(rgb)
        self.font_colour_for_card_type_id = {}
        for card_type_id in self.config()["font_colour"]:
            if not card_type_id in self.component_manager.card_type_with_id:
                continue
            first_key = \
                self.card_type_with_id(card_type_id).fact_keys_and_names[0][0]
            self.font_colour_for_card_type_id[card_type_id] = QtGui.QColor(\
                self.config()["font_colour"][card_type_id][first_key])

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.TextColorRole:
            card_type_id_index = self.index(index.row(), CARD_TYPE_ID)
            card_type_id = unicode(QtSql.QSqlTableModel.data(\
                self, card_type_id_index).toString())
            colour = QtGui.QColor(QtCore.Qt.black)
            if card_type_id in self.font_colour_for_card_type_id:
                colour = self.font_colour_for_card_type_id[card_type_id]
            return QtCore.QVariant(colour)
        if role == QtCore.Qt.BackgroundColorRole:
            card_type_id_index = self.index(index.row(), CARD_TYPE_ID)
            card_type_id = unicode(QtSql.QSqlTableModel.data(\
                self, card_type_id_index).toString())
            if card_type_id in self.background_colour_for_card_type_id:
                return QtCore.QVariant(\
                    self.background_colour_for_card_type_id[card_type_id])
            else:
                return QtCore.QVariant(\
                    QtGui.qApp.palette().color(QtGui.QPalette.Base))
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
        # sorting still uses the orginal database keys, which is good
        # for speed.
        if column == GRADE:
            grade = QtSql.QSqlTableModel.data(self, index).toInt()[0]
            if grade == -1:
                return QtCore.QVariant(_("Yet to learn"))
            else:
                return QtCore.QVariant(grade)
        if column == NEXT_REP:
            next_rep = QtSql.QSqlTableModel.data(self, index, role).toInt()[0]
            if next_rep <= 0:
                return QtCore.QVariant("")
            return QtCore.QVariant(\
                self.scheduler().next_rep_to_interval_string(next_rep))
        if column == LAST_REP:
            last_rep = QtSql.QSqlTableModel.data(self, index, role).toInt()[0]
            if last_rep <= 0:
                return QtCore.QVariant("")
            return QtCore.QVariant(\
                self.scheduler().last_rep_to_interval_string(last_rep))
        if column == EASINESS:
            old_data = QtSql.QSqlTableModel.data(self, index, role).toString()
            return QtCore.QVariant("%.2f" % float(old_data))
        if column in (CREATION_TIME, MODIFICATION_TIME):
            old_data = QtSql.QSqlTableModel.data(self, index, role).toInt()[0]
            return QtCore.QVariant(time.strftime(self.date_format,
                time.localtime(old_data)))
        return QtSql.QSqlTableModel.data(self, index, role)


class QA_Delegate(QtGui.QStyledItemDelegate, Component):

    # http://stackoverflow.com/questions/1956542/
    # how-to-make-item-view-render-rich-html-text-in-qt

    def __init__(self, component_manager, Q_or_A, parent=None):
        Component.__init__(self, component_manager)
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.doc = QtGui.QTextDocument(self)
        self.Q_or_A = Q_or_A

    # We need to reimplement the database access functions here using Qt's
    # database driver. Otherwise, both Qt and libmnemosyne try to claim
    # ownership at the same time. We don't reconstruct everything in order
    # to save time. This could in theory give problems if the browser render
    # chain makes use of this extra information, but that seems unlikely.

    def tag(self, _id):
        query = QtSql.QSqlQuery(\
            "select name from tags where _id=%d" % (_id, ))
        query.first()
        tag = Tag(unicode(query.value(0).toString()), "dummy_id")
        tag._id = _id
        return tag

    def fact(self, _id):
        # Create dictionary with fact.data.
        fact_data = {}
        query = QtSql.QSqlQuery(\
           "select key, value from data_for_fact where _fact_id=%d" % (_id, ))
        query.next()
        while query.isValid():
            fact_data[unicode(query.value(0).toString())] = \
                unicode(query.value(1).toString())
            query.next()
        # Create fact.
        fact = Fact(fact_data, "dummy_id")
        fact._id = _id
        return fact

    def card(self, _id):
        query = QtSql.QSqlQuery("""select _fact_id, card_type_id,
            fact_view_id, extra_data from cards where _id=%d""" % (_id, ))
        query.first()
        fact = self.fact(query.value(0).toInt()[0])
        # Note that for the card type, we turn to the component manager as
        # opposed to this database, as we would otherwise miss the built-in
        # system card types
        card_type = self.card_type_with_id(unicode(query.value(1).toString()))
        fact_view_id = unicode(query.value(2).toString())
        for fact_view in card_type.fact_views:
            if fact_view.id == fact_view_id:
                card = Card(card_type, fact, fact_view)
                # We need extra_data to display the cloze cards.
                extra_data = unicode(query.value(3).toString())
                if extra_data == "":
                    card.extra_data = {}
                else:
                    card.extra_data = eval(extra_data)
                break

        # Let's not add tags to speed things up, they don't affect the card
        # browser renderer

        #query = QtSql.QSqlQuery("""select _tag_id from tags_for_card
        #    where _card_id=%d""" % (_id, ))
        #query.next()
        #while query.isValid():
        #    card.tags.add(self.tag(query.value(0).toInt()[0]))
        #    query.next()

        return card

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
        card = self.card(_id)
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


class BrowseCardsDlg(QtGui.QDialog, Ui_BrowseCardsDlg, BrowseCardsDialog,
                     TipAfterStartingNTimes):

    started_n_times_counter = "started_browse_cards_n_times"
    tip_after_n_times = \
        {3 : _("Right-click on a tag name in the card browser to edit or delete it."),
         6 : _("Double-click on a card or tag name in the card browser to edit them."),
         9 : _("You can reorder columns in the card browser by dragging the header label."),
        12 : _("You can resize columns in the card browser by dragging between the header labels."),
        15 : _("When editing or previewing cards from the card browser, PageUp/PageDown can be used to move to the previous/next card."),
        18 : _("You change the relative size of the card list, card type tree and tag tree by dragging the dividers between them."),
        21 : _("In the search box, you can use SQL wildcards like _ (matching a single character) and % (matching one or more characters).")}

    def __init__(self, component_manager):
        BrowseCardsDialog.__init__(self, component_manager)
        self.show_tip_after_starting_n_times()
        QtGui.QDialog.__init__(self, self.main_widget())
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowContextHelpButtonHint)
        self.saved_index = None
        self.card_model = None
        # Set up card type tree.
        self.container_1 = QtGui.QWidget(self.splitter_1)
        self.layout_1 = QtGui.QVBoxLayout(self.container_1)
        self.label_1 = QtGui.QLabel(_("Show cards from these card types:"),
            self.container_1)
        self.layout_1.addWidget(self.label_1)
        self.card_type_tree_wdgt = \
            CardTypesTreeWdgt(component_manager, self.container_1, 
            self.unload_qt_database)
        self.card_type_tree_wdgt.card_types_changed_signal.\
            connect(self.reload_database_and_redraw)
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
            self.unload_qt_database)
        self.tag_tree_wdgt.tags_changed_signal.\
            connect(self.reload_database_and_redraw) 
        self.layout_2.addWidget(self.tag_tree_wdgt)
        self.label_3 = QtGui.QLabel(_("containing this text in the cards:"),
            self.container_2)
        self.layout_2.addWidget(self.label_3)
        self.search_box = QtGui.QLineEdit(self.container_2)
        self.search_box.textChanged.connect(self.search_text_changed)
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.update_filter)
        self.search_box.setFocus()
        self.layout_2.addWidget(self.search_box)
        self.splitter_1.insertWidget(1, self.container_2)
        # Fill tree widgets.
        criterion = self.database().current_criterion()
        self.card_type_tree_wdgt.display(criterion)
        self.tag_tree_wdgt.display(criterion)
        # When starting the widget, we default with the current criterion
        # as filter. In this case, we can make a shortcut simply by selecting
        # on 'active=1'
        self.load_qt_database()
        self.display_card_table(run_filter=False)
        self.card_model.setFilter("cards.active=1")
        self.card_model.select()
        self.update_card_counters()
        self.card_type_tree_wdgt.tree_wdgt.\
            itemClicked.connect(self.update_filter)
        self.tag_tree_wdgt.tree_wdgt.\
            itemClicked.connect(self.update_filter)        
        # Context menu.
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.context_menu)
        # Restore state.
        state = self.config()["browse_cards_dlg_state"]
        if state:
            self.restoreGeometry(state)
        splitter_1_state = self.config()["browse_cards_dlg_splitter_1_state"]
        if not splitter_1_state:
            self.splitter_1.setSizes([230, 320])
        else:
            self.splitter_1.restoreState(splitter_1_state)
        splitter_2_state = self.config()["browse_cards_dlg_splitter_2_state"]
        if not splitter_2_state:
            self.splitter_2.setSizes([333, 630])
        else:
            self.splitter_2.restoreState(splitter_2_state)   
        for column in (_ID, ID, CARD_TYPE_ID, _FACT_ID, FACT_VIEW_ID,
            ACQ_REPS_SINCE_LAPSE, RET_REPS_SINCE_LAPSE,
            EXTRA_DATA, ACTIVE, SCHEDULER_DATA):
            self.table.setColumnHidden(column, True)

    def context_menu(self, point):
        menu = QtGui.QMenu(self)
        edit_action = QtGui.QAction(_("&Edit"), menu)
        edit_action.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_E)
        edit_action.triggered.connect(self.menu_edit)
        menu.addAction(edit_action)
        preview_action = QtGui.QAction(_("&Preview"), menu)
        preview_action.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_P)
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
        add_tags_action = QtGui.QAction(_("&Add tags"), menu)
        add_tags_action.triggered.connect(self.menu_add_tags)
        menu.addAction(add_tags_action)
        remove_tags_action = QtGui.QAction(_("&Remove tags"), menu)
        remove_tags_action.triggered.connect(self.menu_remove_tags)
        menu.addAction(remove_tags_action)
        indexes = self.table.selectionModel().selectedRows()
        if len(indexes) > 1:
            edit_action.setEnabled(False)
            preview_action.setEnabled(False)
        if len(indexes) >= 1:
            menu.exec_(self.table.mapToGlobal(point))

    def keyPressEvent(self, event):
        if len(self.table.selectionModel().selectedRows()) == 0:
            QtGui.QDialog.keyPressEvent(self, event)
        if event.key() in [QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return]:
            self.menu_edit()
        elif event.key() == QtCore.Qt.Key_E and \
            event.modifiers() == QtCore.Qt.ControlModifier:
            self.menu_edit()
        elif event.key() == QtCore.Qt.Key_P and \
            event.modifiers() == QtCore.Qt.ControlModifier:
            self.menu_preview()
        elif event.key() == QtCore.Qt.Key_F and \
            event.modifiers() == QtCore.Qt.ControlModifier:
            self.search_box.setFocus()
        elif event.key() in [QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace]:
            self.menu_delete()
        else:
            QtGui.QDialog.keyPressEvent(self, event)

    def sister_cards_from_single_selection(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) == 0:
            return []
        index = selected_rows[0]
        _fact_id_index = index.model().index(\
            index.row(), _FACT_ID, index.parent())
        _fact_id = index.model().data(_fact_id_index).toInt()[0]
        fact = self.database().fact(_fact_id, is_id_internal=True)
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
            facts.append(self.database().fact(_fact_id, is_id_internal=True))
        return facts

    def _card_ids_from_selection(self):
        _card_ids = set()
        for index in self.table.selectionModel().selectedRows():
            _card_id_index = index.model().index(\
                index.row(), _ID, index.parent())
            _card_id = index.model().data(_card_id_index).toInt()[0]
            _card_ids.add(_card_id)
        return _card_ids

    def menu_edit(self, index=None):
        # 'index' gets passed if this function gets called through the
        # table.doubleClicked event.
        _card_ids = self._card_ids_from_selection()
        if len(_card_ids) == 0:
            return
        card = self.database().card(_card_ids.pop(), is_id_internal=True)
        self.edit_dlg = self.component_manager.current("edit_card_dialog")\
            (card, self.component_manager, started_from_card_browser=True,
            parent=self)
        # Here, we don't unload the database already by ourselves, but leave
        # it to the edit dialog to only do so if needed.
        self.edit_dlg.before_apply_hook = self.unload_qt_database
        self.edit_dlg.page_up_down_signal.connect(self.page_up_down_edit)
        if self.edit_dlg.exec_() == QtGui.QDialog.Accepted:
            self.card_type_tree_wdgt.rebuild()
            self.tag_tree_wdgt.rebuild()
            self.load_qt_database()
            self.display_card_table()
        # Avoid multiple connections.
        self.edit_dlg.page_up_down_signal.disconnect(self.page_up_down_edit)

    def page_up_down_edit(self, up_down):
        current_row = self.table.selectionModel().selectedRows()[0].row()
        if up_down == self.edit_dlg.UP:
            shift = -1
        elif up_down == self.edit_dlg.DOWN:
            shift = 1
        self.table.selectRow(current_row + shift)
        _card_ids = self._card_ids_from_selection()
        card = self.database().card(_card_ids.pop(), is_id_internal=True)
        self.edit_dlg.set_new_card(card)

    def menu_preview(self):
        from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
        cards = self.sister_cards_from_single_selection()
        tag_text = cards[0].tag_string()
        self.preview_dlg = \
            PreviewCardsDlg(self.component_manager, cards, tag_text, self)
        self.preview_dlg.page_up_down_signal.connect(\
            self.page_up_down_preview)
        self.preview_dlg.exec_()
        # Avoid multiple connections.
        self.preview_dlg.page_up_down_signal.disconnect(\
            self.page_up_down_preview)

    def page_up_down_preview(self, up_down):
        from mnemosyne.pyqt_ui.preview_cards_dlg import PreviewCardsDlg
        current_row = self.table.selectionModel().selectedRows()[0].row()
        if up_down == PreviewCardsDlg.UP:
            shift = -1
        elif up_down == PreviewCardsDlg.DOWN:
            shift = 1
        self.table.selectRow(current_row + shift)
        self.preview_dlg.index = 0
        self.preview_dlg.cards = self.sister_cards_from_single_selection()
        self.preview_dlg.tag_text = self.preview_dlg.cards[0].tag_string()
        self.preview_dlg.update_dialog()

    def menu_delete(self):
        answer = self.main_widget().show_question\
            (_("Go ahead with delete? Sister cards will be deleted as well."),
            _("&OK"), _("&Cancel"), "")
        if answer == 1: # Cancel.
            return
        _fact_ids = set()
        for index in self.table.selectionModel().selectedRows():
            _fact_id_index = index.model().index(\
                index.row(), _FACT_ID, index.parent())
            _fact_id = index.model().data(_fact_id_index).toInt()[0]
            _fact_ids.add(_fact_id)
        facts = []
        for _fact_id in _fact_ids:
            facts.append(self.database().fact(_fact_id, is_id_internal=True))
        self.unload_qt_database()
        self.saved_selection = []
        self.controller().delete_facts_and_their_cards(facts)
        self.card_type_tree_wdgt.rebuild()
        self.tag_tree_wdgt.rebuild()
        self.load_qt_database()
        self.display_card_table()

    def menu_change_card_type(self):
        # Test if all selected cards have the same card type.
        current_card_type_ids = set()
        for index in self.table.selectionModel().selectedRows():
            card_type_id_index = index.model().index(\
                index.row(), CARD_TYPE_ID, index.parent())
            card_type_id = \
                unicode(index.model().data(card_type_id_index).toString())
            current_card_type_ids.add(card_type_id)
            if len(current_card_type_ids) > 1:
                self.main_widget().show_error\
                    (_("The selected cards should have the same card type."))
                return
        current_card_type = self.card_type_with_id(current_card_type_ids.pop())
        # Get new card type. Use a dict as backdoor to return values
        # from the dialog.
        return_values = {}
        from mnemosyne.pyqt_ui.change_card_type_dlg import ChangeCardTypeDlg
        dlg = ChangeCardTypeDlg(self.component_manager,
            current_card_type, return_values, parent=self)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return
        new_card_type = return_values["new_card_type"]
        # Get correspondence.
        self.correspondence = {}
        if not current_card_type.fact_keys().issubset(new_card_type.fact_keys()):
            dlg = ConvertCardTypeKeysDlg(current_card_type, new_card_type,
                self.correspondence, check_required_fact_keys=True, parent=self)
            if dlg.exec_() != QtGui.QDialog.Accepted:
                return
        # Start the actual conversion.
        facts = self.facts_from_selection()
        self.unload_qt_database()
        self.controller().change_card_type(facts, current_card_type,
            new_card_type, self.correspondence)
        self.card_type_tree_wdgt.rebuild()
        self.tag_tree_wdgt.rebuild()
        self.load_qt_database()
        self.display_card_table()

    def menu_add_tags(self):
        if not self.config()["showed_help_on_adding_tags"]:
            self.main_widget().show_information(\
"With this option, can you edit the tags of individual cards, without affecting sister cards.")
            self.config()["showed_help_on_adding_tags"] = True
        # Get new tag names. Use a dict as backdoor to return values
        # from the dialog.
        return_values = {}
        from mnemosyne.pyqt_ui.add_tags_dlg import AddTagsDlg
        dlg = AddTagsDlg(self.component_manager, return_values, parent=self)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return
        # Add the tags.
        _card_ids = self._card_ids_from_selection()
        self.unload_qt_database()
        for tag_name in return_values["tag_names"]:
            if not tag_name:
                continue
            tag = self.database().get_or_create_tag_with_name(tag_name)
            self.database().add_tag_to_cards_with_internal_ids(tag, _card_ids)
        self.tag_tree_wdgt.rebuild()
        self.load_qt_database()
        self.display_card_table()

    def menu_remove_tags(self):
        if not self.config()["showed_help_on_adding_tags"]:
            self.main_widget().show_information(\
"With this option, can you edit the tags of individual cards, without affecting sister cards.")
            self.config()["showed_help_on_adding_tags"] = True
        # Figure out the tags used by the selected cards.
        _card_ids = self._card_ids_from_selection()
        tags = self.database().tags_from_cards_with_internal_ids(_card_ids)
        # Get new tag names. Use a dict as backdoor to return values
        # from the dialog.
        return_values = {}
        from mnemosyne.pyqt_ui.remove_tags_dlg import RemoveTagsDlg
        dlg = RemoveTagsDlg(self, tags, return_values)
        if dlg.exec_() != QtGui.QDialog.Accepted:
            return
        # Remove the tags.
        self.unload_qt_database()
        for tag_name in return_values["tag_names"]:
            if not tag_name:
                continue
            tag = self.database().get_or_create_tag_with_name(tag_name)
            self.database().remove_tag_from_cards_with_internal_ids(\
                tag, _card_ids)
        self.tag_tree_wdgt.rebuild()
        self.load_qt_database()
        self.display_card_table()

    def load_qt_database(self):
        self.database().release_connection()
        qt_db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
        qt_db.setDatabaseName(self.database().path())
        if not qt_db.open():
            QtGui.QMessageBox.warning(None, _("Mnemosyne"),
                _("Database error: ") + qt_db.lastError().text())
            sys.exit(1)

    def unload_qt_database(self):
        # Don't save state twice when closing dialog.
        if self.card_model is None:
            return
        self.saved_index = self.table.indexAt(QtCore.QPoint(0,0))
        self.saved_selection = self.table.selectionModel().selectedRows()
        self.config()["browse_cards_dlg_table_settings"] \
            = self.table.horizontalHeader().saveState()
        self.table.setModel(QtGui.QStandardItemModel())
        del self.card_model
        self.card_model = None
        QtSql.QSqlDatabase.removeDatabase(\
            QtSql.QSqlDatabase.database().connectionName())

    def display_card_table(self, run_filter=True):
        self.card_model = CardModel(self.component_manager)
        self.card_model.setTable("cards")
        headers = {QUESTION: _("Question"), ANSWER: _("Answer"),
            TAGS: _("Tags"), GRADE: _("Grade"), NEXT_REP: _("Next rep"),
            LAST_REP: _("Last rep"), EASINESS: _("Easiness"),
            ACQ_REPS: _("Learning\nreps"),
            RET_REPS: _("Review\nreps"), LAPSES: _("Lapses"),
            CREATION_TIME: _("Created"), MODIFICATION_TIME: _("Modified")}
        for key, value in headers.iteritems():
              self.card_model.setHeaderData(key, QtCore.Qt.Horizontal,
                  QtCore.QVariant(value))
        self.table.setModel(self.card_model)
        self.table.horizontalHeader().sectionClicked.connect(\
            self.horizontal_header_section_clicked)
        table_settings = self.config()["browse_cards_dlg_table_settings"]
        if table_settings:
            self.table.horizontalHeader().restoreState(table_settings)
        self.table.horizontalHeader().setMovable(True)
        self.table.setItemDelegateForColumn(\
            QUESTION, QA_Delegate(self.component_manager, QUESTION, self))
        self.table.setItemDelegateForColumn(\
            ANSWER, QA_Delegate(self.component_manager, ANSWER, self))
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        # Since this function can get called multiple times, we need to make
        # sure there is only a single connection for the double-click event.
        try:
            self.table.doubleClicked.disconnect(self.menu_edit)
        except TypeError:
            pass
        self.table.doubleClicked.connect(self.menu_edit)
        self.table.verticalHeader().hide()
        query = QtSql.QSqlQuery("select count() from tags")
        query.first()
        self.tag_count = query.value(0).toInt()[0]
        if run_filter:
            self.update_filter() # Needed after tag rename.
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
            # Note that there seem to be serious Qt preformance problems with
            # selectRow, so we only do this for a small number of rows.
            if len(self.saved_selection) < 10:
                for index in self.saved_selection:
                    self.table.selectRow(index.row())
            self.table.setSelectionMode(old_selection_mode)

    def reload_database_and_redraw(self):
        self.load_qt_database()
        self.display_card_table()

    def horizontal_header_section_clicked(self, index):
        if not self.config()["browse_cards_dlg_sorting_warning_shown"]:
            self.main_widget().show_information(\
_("You chose to sort this table. Operations in the card browser could now be slower. Next time you start the card browser, the table will be unsorted again."))
            self.config()["browse_cards_dlg_sorting_warning_shown"] = True

    def activate(self):
        self.exec_()

    def search_text_changed(self):
        # Don't immediately start updating the filter, but wait until the last
        # keypress was 300 ms ago.
        self.timer.start(300)

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
        if len(criterion._tag_ids_active) == 0:
            filter = "_id='not_there'"
        elif len(criterion._tag_ids_active) != self.tag_count:
            if filter:
                filter += "and "
            # Determine all _card_ids.
            query = QtSql.QSqlQuery("select _id from cards")
            all__card_ids = set()
            while query.next():
                all__card_ids.add(str(query.value(0).toInt()[0]))
            # Determine _card_ids of card with an active tag.
            query = "select _card_id from tags_for_card where _tag_id in ("
            for _tag_id in criterion._tag_ids_active:
                query += "'%s', " % (_tag_id, )
            query = query[:-2] + ")"
            query = QtSql.QSqlQuery(query)
            active__card_ids = set()
            while query.next():
                active__card_ids.add(str(query.value(0).toInt()[0]))
            # Construct most optimal query.
            if len(active__card_ids) > len(all__card_ids)/2:
                filter += "_id not in (" + \
                    ",".join(all__card_ids - active__card_ids) + ")"
            else:
                filter += "_id in (" + ",".join(active__card_ids) + ")"
        # Search string.
        search_string = unicode(self.search_box.text()).replace("'", "''")
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
            _("%d cards shown, of which %d active.") % (selected, active))

    def _store_state(self):
        self.config()["browse_cards_dlg_state"] = self.saveGeometry()
        self.config()["browse_cards_dlg_splitter_1_state"] = \
            self.splitter_1.saveState()
        self.config()["browse_cards_dlg_splitter_2_state"] = \
            self.splitter_2.saveState()
        # Make sure we start unsorted again next time.
        if not self.config()["start_card_browser_sorted"]:
            self.table.horizontalHeader().setSortIndicator\
                (-1, QtCore.Qt.AscendingOrder)

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()
        self.unload_qt_database()
        # This allows the state of the tag tree to be saved.
        self.tag_tree_wdgt.close()

    def reject(self):
        # Generated when pressing escape.
        self.unload_qt_database()
        return QtGui.QDialog.reject(self)

    def accept(self):
        # 'accept' does not generate a close event.
        self._store_state()
        self.unload_qt_database()
        return QtGui.QDialog.accept(self)
