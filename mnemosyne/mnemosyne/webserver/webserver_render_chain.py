#
# webserver_render_chain.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.filters.html5_media import Html5Media
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.webserver.webserver_renderer import WebserverRenderer
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
     NonLatinFontSizeIncrease


class WebserverRenderChain(RenderChain):

    id = "webserver"

    filters = [EscapeToHtml, Latex, ExpandPaths, Html5Media,
               NonLatinFontSizeIncrease]
    renderers = [WebserverRenderer]
