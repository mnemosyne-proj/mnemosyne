#
# add_RTL_marker.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filter import Filter


class AddRTLMarker(Filter):

    """Add the RTL marker to Arabic and Hebrew text, such that punctuation
    comes out alright.

    Should work e.g. for
        <arabic>[...]
        [...]<arabic>
        <arabic>(<arabic>)
        (<arabic>)<arabic>
    Also if linebreaks are present inbetween.

    The heuristic fails if the string also contains latin text, e.g.
        <english> (<english> <arabic>)

    See http://dotancohen.com/howto/rtl_right_to_left.html

    """

    def run(self, text, card, fact_key, **render_args):
        for i in range(len(text)):
            if 0x0590 <= ord(text[i]) <= 0x06FF:
                return "&rlm;" + text.replace("\n", "&rlm;\n&rlm;").\
                    replace("<br>", "&rlm;<br>&rlm;") + "&rlm;"
        return text
