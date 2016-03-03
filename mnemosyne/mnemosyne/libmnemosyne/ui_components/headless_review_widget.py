#
# headless_review_widget.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget


class HeadlessReviewWidget(ReviewWidget):    

    def redraw_now(self):
        pass