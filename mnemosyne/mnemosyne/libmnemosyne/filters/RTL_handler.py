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

        if len(text) <= 1:
            return text
        # If we are in the first term of a cloze deletion, we need a work-
        # around.
        if text[0] == "[" and text[1] in string.ascii_letters and "]" in text:
            part1, part2 = text.split("]", 1)
            return "<span dir=\"ltr\">" + part1 + "]</span>" + \
                "<span dir=\"rtl\">" + part2 + "</span>"
        # If we start with latin, we'll keep the paragraph ordering as ltr.
        if text[0] in string.ascii_letters or text[1] in string.ascii_letters:
            return text
        # Otherwise, as soon as there is RTL, make everything RTL.
        for i in range(len(text)):
            if 0x0590 <= ord(text[i]) <= 0x06FF:
                return "<span dir=\"rtl\">" + text + "</span>"
        return text
