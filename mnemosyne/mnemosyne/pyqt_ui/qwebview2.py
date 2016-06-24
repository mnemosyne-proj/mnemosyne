#
# qwebview2.py <Peter.Bienstman@UGent.be>
#

import webbrowser
from PyQt5 import QtGui, QtWidgets, QtWebEngineWidgets

from mnemosyne.libmnemosyne.translator import _


class QWebView2(QtWebEngineWidgets.QWebEngineView):

    """QWebView which restores the focus to the review widget,
    so that the keyboard shortcuts still continue to work.

    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.linkClicked.connect(self.link_clicked) 
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
    
    def link_clicked(self, url):
        webbrowser.open(str(url.toString()))
        
    def focusInEvent(self, event):
        if hasattr(self.parent(), "restore_focus"):
            self.parent().restore_focus()
        super().focusInEvent(event)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        action = self.pageAction(QtWebKit.QWebPage.Copy)
        # Note that to get the shortcut work, we need extra code in
        # review_wdgt.py.
        action.setShortcuts(QtGui.QKeySequence(_("Ctrl+C")))
        menu.addAction(action)
        menu.exec_(self.mapToGlobal(event.pos()))

      

