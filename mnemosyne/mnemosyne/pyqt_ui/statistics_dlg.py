#
# statistics_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.ui_components.dialogs import StatisticsDialog


class StatisticsDlg(QtGui.QDialog, StatisticsDialog):

    """A tab widget containing several statistics pages. The number and names
    of the tab pages are determined at run time.

    """

    def __init__(self, component_manager):
        StatisticsDialog.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, self.main_widget())
        self.vbox_layout = QtGui.QVBoxLayout(self)
        self.tab_widget = QtGui.QTabWidget(self.main_widget())
        page_index = 0
        for page in self.statistics_pages():
            page = page(self.component_manager)
            self.tab_widget.addTab(StatisticsPageWdgt(self, component_manager,
                page, page_index), page.name)
            page_index += 1
        self.vbox_layout.addWidget(self.tab_widget)       
        self.button_layout = QtGui.QHBoxLayout()
        self.button_layout.addItem(QtGui.QSpacerItem(20, 20,
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.ok_button = QtGui.QPushButton(_("&OK"), self)
        self.button_layout.addWidget(self.ok_button)
        self.vbox_layout.addLayout(self.button_layout)
        self.connect(self.ok_button, QtCore.SIGNAL("clicked()"), self.accept)
        self.connect(self.tab_widget, QtCore.SIGNAL("currentChanged(int)"),
                     self.display_page)
        page_index = self.config()["last_statistics_page"]
        if page_index >= self.tab_widget.count():
            page_index = 0
        self.tab_widget.setCurrentIndex(page_index)
        self.display_page(page_index)
           
    def activate(self):
        self.exec_()

    def closeEvent(self, event):
        self.config()["statistics_widget_size"] = (self.width(), self.height())
        
    def accept(self):
        self.config()["statistics_widget_size"] = (self.width(), self.height())
        return QtGui.QDialog.accept(self)        
        
    def display_page(self, page_index):
        page = self.tab_widget.widget(page_index)
        self.config()["last_variant_for_statistics_page"].setdefault(page_index, 0)
        variant_index = self.config()["last_variant_for_statistics_page"][page_index]
        if variant_index >= page.combobox.count():
            variant_index = 0
        page.combobox.setCurrentIndex(variant_index)
        page.display_variant(variant_index)
        self.config()["last_statistics_page"] = page_index

        # TODO: suffers from screen corruption
        #width, height = self.config()["main_window_size"]
        #if width:
        #    self.resize(width, height)


class StatisticsPageWdgt(QtGui.QWidget, Component):

    """A page in the StatisticsDlg tab widget. This page widget only contains
    a combobox to select different variants of the page. The widget that
    displays the statistics information itself is only generated when it
    becomes visible.

    """

    def __init__(self, parent, component_manager, statistics_page, page_index):
        Component.__init__(self, component_manager)        
        QtGui.QWidget.__init__(self, parent)
        self.statistics_page = statistics_page
        self.page_index = page_index
        self.vbox_layout = QtGui.QVBoxLayout(self)
        self.combobox = QtGui.QComboBox(self)
        self.variant_ids = []
        self.variant_widgets = []
        self.current_variant_widget = None
        variants = statistics_page.variants
        if not variants:
            variants = [(0, "Default")]
        for variant_id, variant_name in variants:
            self.variant_ids.append(variant_id)
            self.variant_widgets.append(None)
            self.combobox.addItem(str(variant_name))
        if len(self.variant_ids) <= 1 or \
           self.statistics_page.show_variants_in_combobox == False:
            self.combobox.hide()
        self.vbox_layout.addWidget(self.combobox)
        self.connect(self.combobox, QtCore.SIGNAL("currentIndexChanged(int)"),
                     self.display_variant)
        
    def display_variant(self, variant_index):

        "Lazy creation of the actual widget that displays the statistics."

        # Hide the previous widget if there was once.
        if self.current_variant_widget:
            self.vbox_layout.removeWidget(self.current_variant_widget)
            self.current_variant_widget.hide()
        # Create widget if it has not been shown before.
        if not self.variant_widgets[variant_index]:
            self.statistics_page.prepare_statistics\
                (self.variant_ids[variant_index])
            widget_class = self.component_manager.get_current(\
                "statistics_widget", used_for=self.statistics_page.__class__)
            widget = widget_class(self, self.component_manager,
                self.statistics_page)
            widget.show_statistics(self.variant_ids[variant_index])
            self.variant_widgets[variant_index] = widget
        # Show the widget created earlier.
        self.current_variant_widget = self.variant_widgets[variant_index]
        self.vbox_layout.addWidget(self.current_variant_widget)
        self.current_variant_widget.show()
        self.config()["last_variant_for_statistics_page"][self.page_index] = \
           variant_index
