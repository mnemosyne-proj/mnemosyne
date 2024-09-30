#
# sync_to_card_only_client.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml


class SyncToCardOnlyClient(RenderChain):

    """Renders either the question or answer as a complete web page, for
    use by the sync server to pregenerate questions and answers for a sync
    client which has no notion of facts and understands only cards.

    """

    id = "sync_to_card_only_client"

    filters = [EscapeToHtml, Latex]
    renderers = [HtmlCss]
