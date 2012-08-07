#
# RTL_handler.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filter import Filter


class RTLHandler(Filter):

    """Handle RTL for Arabic and Hebrew text, such that e.g. punctuation
    comes out alright.

    Should work e.g. for
        <arabic>[...]
        [...]<arabic>
        <arabic>(<arabic>)
        (<arabic>)<arabic>
    Also if linebreaks are present inbetween.

    [baa][alif]

    The heuristic fails if the string also contains latin text, e.g.
        <english> (<english> <arabic>)

    See http://dotancohen.com/howto/rtl_right_to_left.html

    """

    def run(self, text, card, fact_key, **render_args):
        # If we start with latin, we'll keep the paragraph ordering as ltr.
        if text and not (0x0590 <= ord(text.lstrip("()[]{}")[0]) <= 0x06FF):
            return text
        for i in range(len(text)):
            if 0x0590 <= ord(text[i]) <= 0x06FF:
                return "<p dir=\"rtl\">" + text + "</p>"
        return text
