#
# escape_to_html_for_card_browser.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.filter import Filter


class EscapeToHtmlForCardBrowser(Filter):

    """Make sure tags like img, latex, ... show up as tags."""

    def run(self, text, card, fact_key, **render_args):
        if text:
            text = text.replace("<img", "&lt;img")
            text = text.replace("<latex", "&lt;latex")
            text = text.replace("<audio", "&lt;audio")
            text = text.replace("<video", "&lt;video")
        return text
