#
# card_browser_render_chain.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.html_css_card_browser \
     import HtmlCssCardBrowser
from mnemosyne.libmnemosyne.filters.escape_to_html_for_card_browser \
     import EscapeToHtmlForCardBrowser


class CardBrowserRenderChain(RenderChain):

    """Renders either the question or answer for display in the card browser.

    """

    id = "card_browser"

    filters = [EscapeToHtmlForCardBrowser]
    renderers = [HtmlCssCardBrowser]

