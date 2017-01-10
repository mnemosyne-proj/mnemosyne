#
# qwebengineview2.py <Peter.Bienstman@UGent.be>
#

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

from mnemosyne.libmnemosyne.translator import _


class QWebEngineView2(QtWebEngineWidgets.QWebEngineView):

    """QWebEngineView which restores the focus to the review widget,
    so that the keyboard shortcuts still continue to work.

    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.installEventFilter(self)
        QtWebEngineWidgets.QWebEngineProfile.defaultProfile().\
         setHttpCacheType(QtWebEngineWidgets.QWebEngineProfile.MemoryHttpCache)
        #self.page().profile().setPersistentCookiesPolicy(\
        #    QtWebEngineWidgets.QWebEngineProfile.NoPersistentCookies)
        # self.linkClicked.connect(self.link_clicked) 
        # self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
    
    def eventFilter(self, obj, event):
        # focusInEvent doesn't seem to want to fire, so need a heavier approach.
        if event.type() == QtCore.QEvent.WindowActivate:
            if hasattr(self.parent(), "restore_focus"):
                self.parent().restore_focus()
        # The above doesn't seem to be entirely full-proof...
        if event.type() == QtCore.QEvent.ShortcutOverride:
            if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
                focus_widget = self.parent().focus_widget
                if focus_widget:
                    focus_widget.animateClick()     
        return QtWebEngineWidgets.QWebEngineView.eventFilter(self, obj, event)
    
    def link_clicked(self, url):
        import webbrowser  # Slow import
        webbrowser.open(url.toString())

        