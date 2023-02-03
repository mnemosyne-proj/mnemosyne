#
# main_wdgt.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.pyqt_ui.ui_main_wdgt import Ui_MainWdgt
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

# Note: inheritance from Ui_MainWdgt should come last, as it inherits
# directly from 'object' with supporting a correct super().__init__
# call.

class MainWdgt(QtWidgets.QMainWindow, MainWidget, Ui_MainWdgt):

    def __init__(self, **kwds):
        super().__init__(**kwds)
        self.setupUi(self)
        # Qt designer does not allow setting multiple shortcuts per action.
        self.actionDeleteCurrentCard.setShortcuts\
            ([QtCore.Qt.Key.Key_Delete, QtCore.Qt.Key.Key_Backspace])
        self.status_bar_widgets = []
        self.progress_bar = None
        self.progress_bar_update_interval = 1
        self.progress_bar_last_shown_value = 0

    def _store_state(self):
        self.config()["main_window_state"] = self.saveGeometry()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.LanguageChange:
            self.retranslateUi(self)
        else:
            QtWidgets.QMainWindow.changeEvent(self, event)

    def createPopupMenu(self):
        # Don't create a silly popup menu saying ('toolBar').
        pass

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()

    def activate(self):
        MainWidget.activate(self)
        state = self.config()["main_window_state"]
        if state:
            self.restoreGeometry(state)
        # Dynamically fill study mode menu.
        study_modes = [x for x in self.component_manager.all("study_mode")]
        study_modes.sort(key=lambda x:x.menu_weight)
        study_mode_group = QtGui.QActionGroup(self)
        self.study_mode_for_action = {}
        for study_mode in study_modes:
            action = QtGui.QAction(study_mode.name, self)
            action.setCheckable(True)
            if self.config()["study_mode"] == study_mode.id:
                action.setChecked(True)
            study_mode_group.addAction(action)
            self.menu_Study.addAction(action)
            self.study_mode_for_action[action] = study_mode
        study_mode_group.triggered.connect(self.change_study_mode)
        self.retranslateUi(self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.controller_heartbeat)
        self.timer.start(1000)  # 1 sec.

    def change_study_mode(self, action):
        action.setChecked(True)
        study_mode = self.study_mode_for_action[action]
        self.controller().set_study_mode(study_mode)

    def controller_heartbeat(self):
        # Need late binding to allow for inheritance.
        self.controller().heartbeat()

    def set_window_title(self, text):
        # Qt bug: seems to only work if no title was defined in the *.ui file.
        self.setWindowTitle(text)

    def top_window(self):
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if not widget.__class__.__name__.startswith("Q") and \
                widget.__class__.__name__ != "MainWdgt" and \
                widget.isVisible() == True:
                    return widget
        return self

    def show_information(self, text):
        QtWidgets.QMessageBox.information(self.top_window(), _("Mnemosyne"),
            text)

    def show_question(self, text, option0, option1, option2):
        dialog = QtWidgets.QMessageBox(self.top_window())
        dialog.setIcon(QtWidgets.QMessageBox.Icon.Question)
        dialog.setWindowTitle(_("Mnemosyne"))
        dialog.setText(text)
        button0 = dialog.addButton(option0, QtWidgets.QMessageBox.ButtonRole.ActionRole)
        button1 = dialog.addButton(option1, QtWidgets.QMessageBox.ButtonRole.ActionRole)
        if option2:
            button2 = dialog.addButton(option2, QtWidgets.QMessageBox.ButtonRole.ActionRole)
        dialog.exec()
        if dialog.clickedButton() == button0:
            result = 0
        elif dialog.clickedButton() == button1:
            result = 1
        elif dialog.clickedButton() == button2:
            result = 2
        return result

    def show_error(self, text):
        QtWidgets.QMessageBox.critical(self.top_window(), _("Mnemosyne"), text)

    def handle_keyboard_interrupt(self, text):
        self._store_state()
        QtWidgets.QApplication.exit()

    def default_font_size(self):
        return QtWidgets.QApplication.font().pointSize()

    def get_filename_to_open(self, path, filter, caption=""):
        filename, _ = QtWidgets.QFileDialog.\
            getOpenFileName(self, caption, path, filter)
        return filename

    def get_filename_to_save(self, path, filter, caption=""):
        filename, _ = QtWidgets.QFileDialog.\
            getSaveFileName(self, caption, path, filter)
        return filename

    def set_status_bar_message(self, text):
        self.status_bar.showMessage(text)

    def set_progress_text(self, text):
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
        if not self.progress_bar:
            self.progress_bar = QtWidgets.QProgressDialog(self.top_window())
            self.progress_bar.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
            self.progress_bar.setWindowFlags(QtCore.Qt.WindowType.Dialog \
                | QtCore.Qt.WindowType.CustomizeWindowHint \
                | QtCore.Qt.WindowType.WindowTitleHint \
                & ~ QtCore.Qt.WindowType.WindowCloseButtonHint \
                & ~ QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
            self.progress_bar.setWindowTitle(_("Mnemosyne"))
            self.progress_bar.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
            self.progress_bar.setCancelButton(None)
            self.progress_bar.setMinimumDuration(0)
        self.progress_bar.setLabelText(text)
        self.progress_bar.setRange(0, 0)
        self.progress_bar_update_interval = 1
        self.progress_bar_current_value = 0
        self.progress_bar_last_shown_value = 0
        self.progress_bar.setValue(0)
        self.progress_bar.show()

    def set_progress_range(self, maximum):
        self.progress_bar.setRange(0, maximum)

    def set_progress_update_interval(self, update_interval):
        update_interval = int(update_interval)
        if update_interval == 0:
            update_interval = 1
        self.progress_bar_update_interval = update_interval

    def increase_progress(self, value):
        self.set_progress_value(self.progress_bar_current_value + value)

    def set_progress_value(self, value):
        # There is a possibility that 'value' does not visit all intermediate
        # integer values in the range, so we need to check and store the last
        # shown and the current value here.
        self.progress_bar_current_value = value
        if value - self.progress_bar_last_shown_value >= \
               self.progress_bar_update_interval:
            self.progress_bar.setValue(value)
            self.progress_bar_last_shown_value = value
            # This automatically processes events too. Calling processEvents
            # explictly here might even cause some crashes.

    def close_progress(self):
        if self.progress_bar:
            self.progress_bar.close()
        self.progress_bar = None

    def enable_edit_current_card(self, is_enabled):
        self.actionEditCurrentCard.setEnabled(is_enabled)

    def enable_delete_current_card(self, is_enabled):
        self.actionDeleteCurrentCard.setEnabled(is_enabled)

    def enable_reset_current_card(self, is_enabled):
        self.actionResetCurrentCard.setEnabled(is_enabled)

    def enable_browse_cards(self, is_enabled):
        self.actionBrowseCards.setEnabled(is_enabled)

    def add_to_status_bar(self, widget):
        self.status_bar_widgets.append(widget)
        self.status_bar.addPermanentWidget(widget)

    def clear_status_bar(self):
        for widget in self.status_bar_widgets:
            self.status_bar.removeWidget(widget)
        self.status_bar_widgets = []

    def file_new(self):
        self.controller().show_new_file_dialog()

    def file_open(self):
        self.controller().show_open_file_dialog()

    def file_save(self):
        self.controller().save_file()

    def file_save_as(self):
        self.controller().show_save_file_as_dialog()

    def compact_database(self):
        self.controller().show_compact_database_dialog()

    def import_file(self):
        self.controller().show_import_file_dialog()

    def export_file(self):
        self.controller().show_export_file_dialog()

    def import_file(self):
        self.controller().show_import_file_dialog()

    def sync(self):
        self.controller().show_sync_dialog()

    def add_cards(self):
        self.controller().show_add_cards_dialog()

    def edit_current_card(self):
        self.controller().show_edit_card_dialog()

    def delete_current_card(self):
        self.controller().delete_current_card()

    def reset_current_card(self):
        self.controller().reset_current_card()

    def browse_cards(self):
        self.controller().show_browse_cards_dialog()

    def activate_cards(self):
        self.controller().show_activate_cards_dialog()

    def find_duplicates(self):
        self.controller().find_duplicates()

    def manage_card_types(self):
        self.controller().show_manage_card_types_dialog()

    def configure(self):
        self.controller().show_configuration_dialog()

    def set_card_appearance(self):
        self.controller().show_card_appearance_dialog()

    def manage_plugins(self):
        self.controller().show_manage_plugins_dialog()

    def show_statistics(self):
        self.controller().show_statistics_dialog()

    def show_getting_started(self):
        self.controller().show_getting_started_dialog()

    def show_tip(self):
        self.controller().show_tip_dialog()

    def show_about(self):
        self.controller().show_about_dialog()
