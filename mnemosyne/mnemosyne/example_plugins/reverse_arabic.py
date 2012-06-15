#
# reverse_arabic.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.plugin import Plugin
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
    NonLatinFontSizeIncrease

class ReverseArabic(Filter):

    def run(self, text, card, fact_key, **render_args):
        for i in range(len(text)):
            if  0x0600 <= ord(text[i]) <= 0x06FF:
                text = text[::-1]
                break
        return text


class ReverseArabicPlugin(Plugin):

    name = "Reverse Arabic"
    description = "Reverse the Arabic in the webserver, to compensate for the fact that the Android browser renders Arabic from left to right."
    components = [ReverseArabic]

    def activate(self):
        Plugin.activate(self)
        try:
            self.render_chain("webserver").\
                register_filter(ReverseArabic, in_front=False)
            self.render_chain("webserver").\
                unregister_filter(NonLatinFontSizeIncrease)
        except KeyError:  # The webserver chain is not active.
            pass

    def deactivate(self):
        Plugin.deactivate(self)
        try:
            self.render_chain("webserver").\
                unregister_filter(ReverseArabic)
            self.render_chain("webserver").\
                register_filter(NonLatinFontSizeIncrease, in_front=False)
        except KeyError:  # The webserver chain is not active.
            pass

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(ReverseArabicPlugin)
