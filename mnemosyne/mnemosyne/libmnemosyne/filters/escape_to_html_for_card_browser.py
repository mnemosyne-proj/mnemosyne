#
# escape_to_html_for_card_browser.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filter import Filter


class EscapeToHtmlForCardBrowser(Filter):

    """Make sure tags like img, latex, ... show up as tags, but honour some
    basic formatting tags.

    """

    def run(self, text, card, fact_key, **render_args):
        text = text.replace("<img", "&lt;img")
        text = text.replace("<audio", "&lt;audio")   
        text = text.replace("<video", "&lt;video")  
        return text
        
        text = text.replace("<", "&lt;")
        text = text.replace("&lt;b>", "<b>")
        text = text.replace("&lt;/b>", "</b>")
        text = text.replace("&lt;B>", "<B>")
        text = text.replace("&lt;/B>", "</B>")
        text = text.replace("&lt;i>", "<i>")
        text = text.replace("&lt;/i>", "</i>")
        text = text.replace("&lt;I>", "<I>")
        text = text.replace("&lt;/I>", "</I>")
        return text

