
#
# custom_tag.py <Peter.Bienstman@gmail.com>
#

import subprocess

from mnemosyne.libmnemosyne.filter import Filter
from mnemosyne.libmnemosyne.plugin import Plugin


class CustomTag(Filter):

    tag_name = "my_tag"
    tag_program = ["/bin/cat", "--show-ends"]

    """This plugin could run several times when a card is displayed,
    so we need to make sure that we run the program only once per card.

    """

    def __init__(self, component_manager):
        Filter.__init__(self, component_manager)
        self.last_filename = None

    def run(self, text, card, fact_key, **render_args):
        if "no_side_effects" in render_args and \
            render_args["no_side_effects"] == True:
            return text
        i = text.lower().find(self.tag_name + " src")
        while i != -1:
            start = text.find("\"", i)
            end = text.find("\"", start + 1)
            if end == -1:
                return text
            filename = text[start+1:end].replace("file://", "")
            if filename == self.last_filename:
                return text
            try:
                subprocess.call(self.tag_program + [filename])
            except:
                self.main_widget.show_error("Unable to open ", filename)
            self.last_filename = filename
            i = text.lower().find(self.tag_name + " src", i + 1)
        return text


class CustomTagPlugin(Plugin):

    name = "Custom tag"
    description = "Intercepts custom tags like <my_tag src=\"filename\"> and runs them in an external program.\n\nEdit the source to customise."
    components = [CustomTag]
    supported_API_level = 3

    def activate(self):
        Plugin.activate(self)
        self.render_chain("default").\
            register_filter(CustomTag, in_front=False)
        # Other chain you might want to add to is e.g. "card_browser".

    def deactivate(self):
        Plugin.deactivate(self)
        self.render_chain("default").\
            unregister_filter(CustomTag)

# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
register_user_plugin(CustomTagPlugin)
