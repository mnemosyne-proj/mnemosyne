#
# plain_text_chain.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.plain_text import PlainText


class PlainTextChain(RenderChain):

    id = "plain_text"

    filters = []
    renderers = [PlainText]
