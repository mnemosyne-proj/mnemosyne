#
# add_RTL_marker.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filter import Filter


class AddRTLMarker(Filter):

    """Add the RTL marker to Arabic and Hebrew text, such that punctuation
    comes out alright.

    See http://dotancohen.com/howto/rtl_right_to_left.html"""

    def run(self, text, card, fact_key, **render_args):
        for i in range(len(text)):
            if 0x0590 <= ord(text[i]) <= 0x06FF:
                return text + "&rlm;"
        return text
