#
# non_latin_font_size_increase.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.card_types.vocabulary import Vocabulary


class NonLatinFontSizeIncrease(Filter):

    """Increase size of non-latin characters. A simple, card-level wide
    alternative to putting cloning card types from Vocabulary.

    Note: card types which derive from Vocabulary override this setting.

    """

    def is_in_latin_plane(self, unicode_char):
        # Basic Latin (US-ASCII): {U+0000..U+007F}
        # Latin-1 (ISO-8859-1): {U+0080..U+00FF}
        # Latin Extended: {U+0100..U+024F}
        # IPA Extensions: {U+0250..U+02AF}\
        # Spacing Modifier Letters: {U+02B0..U+02FF}
        # Combining Diacritical Marks: {U+0300..U+036F}
        # Greek: {U+0370..U+03FF}
        # Cyrillic: {U+0400..U+04FF}
        # Latin Extended Additional
        # Greek Extended
        for plane in [(0x0000, 0x04FF), (0x1E00, 0x1EFF), (0x1F00, 0x1FFF)]:
            if plane[0] < ord(unicode_char) < plane[1]:
                return True
        return False

    def run(self, text, card, fact_key, **render_args):
        if text == "" or self.config()["non_latin_font_size_increase"] == 0:
            return text
        if issubclass(type(card.card_type), Vocabulary) and not \
            isinstance(type(card.card_type), Vocabulary):
            return text
        if fact_key not in card.card_type.fact_key_format_proxies():
            return text
        proxy_key = card.card_type.fact_key_format_proxies()[fact_key]
        font_string = self.config().card_type_property(\
            "font", card.card_type, proxy_key)
        
        if font_string:
            style = ""
            if font_string.count(",") == 9:
                family,size,x,x,w,i,u,s,x,x = font_string.split(",")
            elif font_string.count(",") == 10:
                family,size,x,x,w,i,u,s,x,x,x = font_string.split(",")
            elif font_string.count(",") == 15:
                family,size,x,x,w,i,u,s,x,x,x,x,x,x,x,style \
                    = font_string.split(",")
            else:
                #Segoe UI,11,-1,5,400,0,0,0,0,0,0,0,0,0,0,1,Regular
                #Segoe UI,26,-1,5,700,1,1,1,0,0,0,0,0,0,0,1,Bold Italic
                family,size,x,x,w,i,u,s,x,x,x,x,x,x,x,x,style \
                    = font_string.split(",")
            base_font_size = int(size)
        else:
            base_font_size = self.main_widget().default_font_size()
        non_latin_size = base_font_size + \
            self.config()["non_latin_font_size_increase"]
        new_text = ""
        in_tag = False
        in_protect = 0
        in_unicode_substring = False
        for i in range(len(text)):
            if not self.is_in_latin_plane(text[i]) and not in_protect:
                # Don't substitute within XML tags or file names get
                # messed up.
                if in_tag or in_unicode_substring == True:
                    new_text += text[i]
                else:
                    in_unicode_substring = True
                    new_text += "<font style=\"font-size:" + \
                        str(non_latin_size) + "pt\">" + text[i]
            else:
                # First check for tag start/end.
                if text[i] == "<":
                    in_tag = True
                elif text[i] == ">":
                    in_tag = False
                # Test for <protect> tags.
                if text[i:].startswith("<protect>"):
                    in_protect += 1
                elif text[i:].startswith("</protect>"):
                    in_protect = max(0, in_protect - 1)
                # Close tag.
                if in_unicode_substring == True:
                    in_unicode_substring = False
                    new_text += "</font>" + text[i]
                else:
                    new_text += text[i]
        # Make sure to close the last tag.
        if not self.is_in_latin_plane(text[-1]) and not in_protect:
            new_text += "</font>"
        # Now we can strip all the <protect> tags.
        new_text = new_text.replace("<protect>", "").replace("</protect>", "")
        return new_text
