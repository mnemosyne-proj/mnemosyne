#
# statistics_wdgt_html.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtCore, QtWebEngineWidgets

from mnemosyne.libmnemosyne.statistics_page import HtmlStatisticsPage
from mnemosyne.libmnemosyne.ui_components.statistics_widget import \
     StatisticsWidget


class HtmlStatisticsWdgt(QtWebEngineWidgets.QWebEngineView, StatisticsWidget):

    used_for = HtmlStatisticsPage

    def __init__(self, page, **kwds):
        super().__init__(**kwds)
        self.page = page

    def show_statistics(self, variant):
        self.setHtml(self.page.html)
