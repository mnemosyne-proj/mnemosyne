#
# card_browser_render_chain.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.html_css_card_browser \
     import HtmlCssCardBrowser
from mnemosyne.libmnemosyne.filters.escape_to_html_for_card_browser \
     import EscapeToHtmlForCardBrowser
from mnemosyne.libmnemosyne.filters.RTL_handler import RTLHandler


class CardBrowserRenderChain(RenderChain):

    """Renders either the question or answer for display in the card browser.

    """

    id = "card_browser"

    never_join_q_to_a = True

    filters = [EscapeToHtmlForCardBrowser, RTLHandler]
    renderers = [HtmlCssCardBrowser]

