#
# RTL_handler.py <Peter.Bienstman@gmail.com>
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
        # Deal with corner cases.
        if len(text) <= 1:
            return text
        text = text.strip()
        has_rtl = False
        for i in range(len(text)):
            if 0x0590 <= ord(text[i]) <= 0x06FF:
                has_rtl = True
                break
        if not has_rtl:
            return text
        # If we are in the first term of a cloze deletion, we need a work-
        # around.

        # TODO: seems to have been fixed in current versions of web toolkit?
        if text[0] == "[" and text[1] in string.ascii_letters and "]" in text:
            part1, part2 = text.split("]", 1)
            return "<span dir=\"rtl\">" + part2 + "</span>" + \
                   "<span dir=\"ltr\"> " + part1 + "]</span>"

        # If we start with latin, we'll keep the paragraph ordering as ltr.
        if text[0] in string.ascii_letters or \
           (len(text) >= 2 and text[1] in string.ascii_letters):
            return text
        # Otherwise, make everything RTL.
        return "<span dir=\"rtl\">" + text + "</span>"
