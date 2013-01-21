#
# RTL_handler.py <Peter.Bienstman@UGent.be>
#

import string

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

    <english> (<english> <arabic>)

    See http://dotancohen.com/howto/rtl_right_to_left.html

    """

    def run(self, text, card, fact_key, **render_args):
        # If we start with latin, we'll keep the paragraph ordering as ltr.
        if len(text) <= 1:
            return text
        if text[0] in string.ascii_letters or text[1] in string.ascii_letters:
            return text
        # Otherwise, as soon as there is RTL, make everything RTL.
        for i in range(len(text)):
            if 0x0590 <= ord(text[i]) <= 0x06FF:
                return "<span dir=\"rtl\">" + text + "</span>"
        return text
