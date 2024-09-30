#
# activate_cards_on_rollover.py <Peter.Bienstman@gmail.com>
#

# Assumes you have a set of cards belonging to inactive tags, which you
# want to gradually activate, and an activate tag called "Enabled".
# The following script will add this tag "Enabled" to a few of these cards.

enabled_tag_name = "Enabled"
inactive_tag_names_contain = "my_tag"
number_of_cards_to_activate = 6

from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.plugin import Plugin

class ActivateHook(Hook):

    used_for = "at_rollover"

    def run(self):
        db = self.database()
        enabled_tag = db.get_or_create_tag_with_name(enabled_tag_name)
        for cursor in db.con.execute(""" select _id from cards where active=0
          and tags like '%{}%' order by _id limit ?""".\
          format(inactive_tag_names_contain),
          (number_of_cards_to_activate, )).fetchall():
            card = db.card(cursor[0], is_id_internal=True)
            card.tags.add(enabled_tag)
            db.update_card(card)
        db.save()


class ActivateHookPlugin(Plugin):

    name = "Activate cards on rollover"
    description = "Trickles in a number of cards on rollover. Parameters are set in the Python script."
    components = [ActivateHook]
    supported_API_level = 3


# Register plugin.

from mnemosyne.libmnemosyne.plugin import register_user_plugin
plugin = register_user_plugin(ActivateHookPlugin)

# Since this is typically run on a server with GUI, we automatically
# activate it here.

# TODO: after the first activation, this will actually result in this
# plugin to be activated twice, but this has no effect in this case.

plugin.activate()
