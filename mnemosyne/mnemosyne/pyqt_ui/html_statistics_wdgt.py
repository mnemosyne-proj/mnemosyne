#
# html_statistics_wdgt.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtCore, QtWebKit

from mnemosyne.libmnemosyne.statistics_page import HtmlStatisticsPage
from mnemosyne.libmnemosyne.ui_components.statistics_widget import \
     StatisticsWidget


class HtmlStatisticsWdgt(QtWebKit.QWebView, StatisticsWidget):

    used_for = HtmlStatisticsPage
    
    def __init__(self, parent, component_manager, page):
        StatisticsWidget.__init__(self, component_manager)
        QtWebKit.QWebView.__init__(self, parent)
        self.page = page

    def sizeHint(self):
        return QtCore.QSize(400, 320)

    def show_statistics(self, variant):
        self.setHtml(self.page.html)
