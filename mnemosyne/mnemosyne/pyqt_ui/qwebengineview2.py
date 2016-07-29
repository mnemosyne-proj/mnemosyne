#
# qwebengineview2.py <Peter.Bienstman@UGent.be>
#

import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

from mnemosyne.libmnemosyne.translator import _


class QWebEngineView2(QtWebEngineWidgets.QWebEngineView):

    """QWebEngineView which restores the focus to the review widget,
    so that the keyboard shortcuts still continue to work.

    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.installEventFilter(self)
        # self.linkClicked.connect(self.link_clicked) 
        # self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
    
    def link_clicked(self, url):
        webbrowser.open(url.toString())
        
    def focusInEvent(self, event):
        if hasattr(self.parent(), "restore_focus"):
            self.parent().restore_focus()
        super().focusInEvent(event)

        