#
# statistics_wdgt_html.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtWebKit

from mnemosyne.libmnemosyne.statistics_page import HtmlStatisticsPage
from mnemosyne.libmnemosyne.ui_components.statistics_widget import \
     StatisticsWidget


class HtmlStatisticsWdgt(QtWebKit.QWebView, StatisticsWidget):

    used_for = HtmlStatisticsPage
    
    def __init__(self, component_manager, parent, page):
        super().__init__(parent, component_manager=component_manager)
        self.page = page

    def sizeHint(self):
        return QtCore.QSize(400, 320)

    def show_statistics(self, variant):
        self.setHtml(self.page.html)
