#
# statistics_dlg.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtGui, QtWidgets

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.ui_statistics_dlg import Ui_StatisticsDlg
from mnemosyne.libmnemosyne.ui_components.dialogs import StatisticsDialog


class StatisticsDlg(QtWidgets.QDialog, StatisticsDialog, Ui_StatisticsDlg):

    """A tab widget containing several statistics pages. The number and names
    of the tab pages are determined at run time.

    """

    def __init__(self, **kwds):
        super().__init__(**kwds)

    def activate(self):
        StatisticsDialog.activate(self)
        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() \
            | QtCore.Qt.WindowType.WindowMinMaxButtonsHint)
        self.setWindowFlags(self.windowFlags() \
            & ~ QtCore.Qt.WindowType.WindowContextHelpButtonHint)
        previous_page_index = self.config()["previous_statistics_page"]
        page_index = 0
        for page in self.component_manager.all("statistics_page"):
            page = page(component_manager=self.component_manager)
            self.tab_widget.addTab(StatisticsPageWdgt(page, page_index,
                parent=self, component_manager=self.component_manager),
                                   _(page.name))
            page_index += 1
        self.tab_widget.tabBar().setVisible(self.tab_widget.count() > 1)
        if previous_page_index >= self.tab_widget.count():
            previous_page_index = 0
        self.tab_widget.setCurrentIndex(previous_page_index)
        self.display_page(previous_page_index)
        state = self.config()["statistics_dlg_state"]
        if state:
            self.restoreGeometry(state)
        # Only now do we connect the signal in order to have lazy
        # instantiation.
        self.tab_widget.currentChanged[int].connect(self.display_page)
        self.exec()

    def _store_state(self):
        self.config()["statistics_dlg_state"] = self.saveGeometry()

    def closeEvent(self, event):
        # Generated when clicking the window's close button.
        self._store_state()

    def accept(self):
        # 'accept' does not generate a close event.
        self._store_state()
        return QtWidgets.QDialog.accept(self)

    def reject(self):
        self._store_state()
        return QtWidgets.QDialog.reject(self)

    def display_page(self, page_index):
        page = self.tab_widget.widget(page_index)
        self.config()["previous_statistics_page"] = page_index
        self.config()["previous_variant_for_statistics_page"]\
            .setdefault(page_index, 0)
        variant_index = self.config()\
            ["previous_variant_for_statistics_page"][page_index]
        if variant_index >= page.combobox.count():
            variant_index = 0
        page.combobox.setCurrentIndex(variant_index)
        page.display_variant(variant_index)


class StatisticsPageWdgt(QtWidgets.QWidget, Component):

    """A page in the StatisticsDlg tab widget. This page widget only contains
    a combobox to select different variants of the page. The widget that
    displays the statistics information itself is only generated when it
    becomes visible.

    """

    def __init__(self, statistics_page, page_index, **kwds):
        super().__init__(**kwds)
        self.statistics_page = statistics_page
        self.page_index = page_index
        self.vbox_layout = QtWidgets.QVBoxLayout(self)
        self.combobox = QtWidgets.QComboBox(self)
        self.variant_ids = []
        self.variant_widgets = []
        self.current_variant_widget = None
        variants = statistics_page.variants
        if not variants:
            variants = [(0, _("Default"))]
        for variant_id, variant_name in variants:
            self.variant_ids.append(variant_id)
            self.variant_widgets.append(None)
            self.combobox.addItem(_(variant_name))
        if len(self.variant_ids) <= 1 or \
           self.statistics_page.show_variants_in_combobox == False:
            self.combobox.hide()
        self.vbox_layout.addWidget(self.combobox)
        self.combobox.currentIndexChanged.connect(self.display_variant)

    def display_variant(self, variant_index):

        """Lazy creation of the actual widget that displays the statistics."""

        # Hide the previous widget if there was once.
        if self.current_variant_widget:
            self.vbox_layout.removeWidget(self.current_variant_widget)
            self.current_variant_widget.hide()
        # Create widget if it has not been shown before.
        if not self.variant_widgets[variant_index]:
            self.statistics_page.prepare_statistics\
                (self.variant_ids[variant_index])
            widget_class = self.component_manager.current(\
                "statistics_widget", used_for=self.statistics_page.__class__)
            widget = widget_class(component_manager=self.component_manager,
                parent=self, page=self.statistics_page)
            widget.show_statistics(self.variant_ids[variant_index])
            self.variant_widgets[variant_index] = widget
        # Show the widget created earlier.
        self.current_variant_widget = self.variant_widgets[variant_index]
        self.vbox_layout.addWidget(self.current_variant_widget)
        self.current_variant_widget.show()
        self.config()["previous_variant_for_statistics_page"]\
           [self.page_index] = variant_index
