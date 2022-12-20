#
# web_server_render_chain.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.web_server.simple_html5_audio import SimpleHtml5Audio
#from mnemosyne.web_server.jquery_mb_html5_audio import JQueryMbHtml5Audio
#from mnemosyne.libmnemosyne.filters.html5_audio import Html5Audio
from mnemosyne.libmnemosyne.filters.html5_video import Html5Video
from mnemosyne.web_server.web_server_renderer import WebServerRenderer
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
     NonLatinFontSizeIncrease


class WebServerRenderChain(RenderChain):

    id = "web_server"

    filters = [Latex, EscapeToHtml,
                SimpleHtml5Audio,
                #JQueryMbHtml5Audio,
                #Html5Audio,
                Html5Video, NonLatinFontSizeIncrease]
    renderers = [WebServerRenderer]
