#
# statistics_dlg.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtGui

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.pyqt_ui.matplotlib_canvas import MatplotlibCanvas


class StatisticsDlg(QtGui.QDialog, Component):

    """A tab widget containing several statistics pages. The number and names
    of the tab pages are determined at run time.

    """

    def __init__(self, parent, component_manager):
        Component.__init__(self, component_manager)
        QtGui.QDialog.__init__(self, parent)
        self.vbox_layout = QtGui.QVBoxLayout(self)
        self.tab_widget = QtGui.QTabWidget(parent)
        for page in self.statistics_pages():
            page = page(self.component_manager)
            self.tab_widget.addTab(StatisticsPageWdgt(self, page), page.name)
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
        self.display_page(0)

    def display_page(self, page_index):
        page = self.tab_widget.widget(page_index)
        page.combobox.setCurrentIndex(0)
        page.display_variant(0)
        

class StatisticsPageWdgt(QtGui.QWidget):

    """A page in the StatisticsDlg tab widget. This page widget only contains
    a combobox to select different variants of the page. The widget that
    displays the statistics information itself is only generated when it
    becomes visible.

    """

    def __init__(self, parent, statistics_page):
        QtGui.QWidget.__init__(self, parent)
        self.statistics_page = statistics_page
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
        
        print 'display page', self.statistics_page, 'variant', variant_index
        if self.current_variant_widget:
            self.vbox_layout.removeWidget(self.current_variant_widget)
            self.current_variant_widget.hide()
        if not self.variant_widgets[variant_index]:
            print 'creating page', self.statistics_page.name, 'variant', variant_index
            self.statistics_page.prepare(self.variant_ids[variant_index])
            try:                                                                    
                widget = self.component_manager.get_current("ui_component", \
                    used_for=self.statistics_page.__class__)\
                        (self, self.component_manager)
            except:
                if self.statistics_page.plot_type in \
                    ("barchart", "histogram", "piechart"):
                    widget = MatplotlibCanvas(self, self.statistics_page)
                    widget.show_plot()
                else: # TODO: create html widget
                    pass
            self.variant_widgets[variant_index] = widget
        self.current_variant_widget = self.variant_widgets[variant_index]
        self.vbox_layout.addWidget(self.current_variant_widget)
        self.current_variant_widget.show()
