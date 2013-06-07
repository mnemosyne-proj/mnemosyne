#
# webserver_render_chain.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.webserver.simple_html5_audio import SimpleHtml5Audio
from mnemosyne.libmnemosyne.filters.html5_video import Html5Video
from mnemosyne.webserver.webserver_renderer import WebserverRenderer
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
     NonLatinFontSizeIncrease



class WebserverRenderChain(RenderChain):

    id = "webserver"

    filters = [Latex, EscapeToHtml, SimpleHtml5Audio, Html5Video,
               NonLatinFontSizeIncrease]
    renderers = [WebserverRenderer]
