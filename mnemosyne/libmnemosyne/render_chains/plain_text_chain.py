#
# plain_text_chain.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.render_chain import RenderChain
from mnemosyne.libmnemosyne.renderers.plain_text import PlainText


class PlainTextChain(RenderChain):

    id = "plain_text"

    never_join_q_to_a = True

    filters = []
    renderers = [PlainText]
