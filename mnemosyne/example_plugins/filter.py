#
# filter.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.plugin import Plugin


class AlignImgTop(Filter):

    def run(self, text, card, fact_key, **render_args):
        return text.replace("<img", "<img align=\"top\"")


class AlignImgTopPlugin(Plugin):

    name = "Top align images"
    description = "Align all your images to the top"
    components = [AlignImgTop]
    supported_API_level = 3
    
    def activate(self):
        Plugin.activate(self)
        self.render_chain("default").\
            register_filter(AlignImgTop, in_front=False)
        # Other chain you might want to add to is e.g. "card_browser".

    def deactivate(self):
        Plugin.deactivate(self)
        self.render_chain("default").\
            unregister_filter(AlignImgTop)

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(AlignImgTopPlugin)
