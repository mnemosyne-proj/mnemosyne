#
# qwebengineview2.py <Peter.Bienstman@gmail.com>
#

from PyQt6 import QtWebEngineWidgets

from mnemosyne.libmnemosyne.gui_translator import _


class QWebEngineView2(QtWebEngineWidgets.QWebEngineView):

    """QWebEngineView which restores the focus to the review widget,
    so that the keyboard shortcuts still continue to work.

    """

    def __init__(self, parent=None):
        super().__init__(parent)
        #QtWebEngineWidgets.QWebEngineProfile.defaultProfile().\
        # setHttpCacheType(QtWebEngineWidgets.QWebEngineProfile.MemoryHttpCache)
        #self.page().profile().setPersistentCookiesPolicy(\
        #    QtWebEngineWidgets.QWebEngineProfile.NoPersistentCookies)
        # self.linkClicked.connect(self.link_clicked)
        # self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)

    def link_clicked(self, url):
        import webbrowser  # Slow import
        webbrowser.open(url.toString())

