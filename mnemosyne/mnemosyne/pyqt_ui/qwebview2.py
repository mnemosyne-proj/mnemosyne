#
# qwebview2.py <Peter.Bienstman@UGent.be>
#

from PyQt4 import QtWebKit


class QWebView2(QtWebKit.QWebView):

    """QWebView which restores the focus to the review widget,
    so that the keyboard shortcuts still continue to work.

    """
    
    def focusInEvent(self, event):
        self.parent().restore_focus()
        QtWebKit.QWebView.focusInEvent(self, event)
