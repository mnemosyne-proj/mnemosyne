#
# find_and_replace.py <Peter.Bienstman@gmail.com>
#

import copy
from mnemosyne.script import Mnemosyne

# 'data_dir = None' will use the default system location, edit as appropriate.
data_dir = None
mnemosyne = Mnemosyne(data_dir)

find_string = "\xa0"
replace_string = " "

for _card_id, _fact_id in mnemosyne.database().cards():
    card = mnemosyne.database().card(_card_id, is_id_internal=True)
    changed = False
    new_fact_data = copy.copy(card.fact.data)
    for fact_key in card.fact.data:
        if find_string in card.fact[fact_key]:
            new_fact_data[fact_key] = \
                card.fact[fact_key].replace(find_string, replace_string)
            print((new_fact_data[fact_key]))
            changed = True
    if changed:
        mnemosyne.controller().edit_card_and_sisters(card, new_fact_data,
            card.card_type, [tag.name for tag in card.tags], {})
mnemosyne.finalise()
