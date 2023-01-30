#
# review_wdgt_cramming.py <Peter.Bienstman@gmail.com>
#

import _main_widget


from mnemosyne.android_python.review_widget import ReviewWdgt


class ReviewWdgtCramming(ReviewWdgt):

    def update_status_bar_counters(self):
        wrong_count, unseen_count, active_count = \
                   self.review_controller().counters()
        counters = "Wrong: %d Unseen: %d Active: %d" % \
                    (wrong_count, unseen_count, active_count)
        _main_widget.set_status_bar_message(counters)

