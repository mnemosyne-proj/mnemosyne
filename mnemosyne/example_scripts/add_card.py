#
# add_card.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.script import Mnemosyne

# 'data_dir = None' will use the default system location, edit as appropriate.
data_dir = None
mnemosyne = Mnemosyne(data_dir)

# For info on the card types and their different fields, see
# libmnemosyne/card_types
fact_data = {"f": "front", "b": "back"}
card_type = mnemosyne.card_type_with_id("1")
mnemosyne.controller().create_new_cards(fact_data,
    card_type, grade=4, tag_names=["tag_1", "tag_2"])

mnemosyne.finalise()
