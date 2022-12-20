#
# pyqt_render_chain.py <Peter.Bienstman@gmail.com>
#

import sys

from mnemosyne.libmnemosyne.filters.latex import Latex
from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.html_css import HtmlCss
from mnemosyne.libmnemosyne.filters.RTL_handler import RTLHandler
#from mnemosyne.libmnemosyne.filters.html5_audio import Html5Audio
#from mnemosyne.libmnemosyne.filters.html5_video import Html5Video
from mnemosyne.libmnemosyne.filters.expand_paths import ExpandPaths
from mnemosyne.libmnemosyne.filters.escape_to_html import EscapeToHtml
from mnemosyne.libmnemosyne.filters.non_latin_font_size_increase import \
     NonLatinFontSizeIncrease
from mnemosyne.pyqt_ui.mplayer_audio import MplayerAudio
from mnemosyne.pyqt_ui.mplayer_video import MplayerVideo

class PyQtRenderChain(RenderChain):

    id = "default"
    
    filters = [Latex, EscapeToHtml, ExpandPaths, MplayerAudio,
        MplayerVideo, RTLHandler, NonLatinFontSizeIncrease]
    
    # Note: the sound system under Debian seems broken now, so we
    # resort to mplayer everywhere.
        
    #    filters = [Latex, EscapeToHtml, ExpandPaths, Html5Audio,
    #            Html5Video, RTLHandler, NonLatinFontSizeIncrease]

    renderers = [HtmlCss]
