#
# export_to_pdf.py <Peter.Bienstman@gmail.com>
#

# Quick and dirty script to export the latest 100 Arabic cards to a pdf file
# Requires unoconv from libreoffice.

# 'data_dir = None' will use the default sysem location, edit as appropriate.
data_dir = None
cards_to_export = 100
text_in_tag = "Arabic"

import os

from mnemosyne.script import Mnemosyne
mnemosyne = Mnemosyne(data_dir)

f = file("mnemosyne.txt", "w")
    
_fact_ids = []
count = 0
for cursor in mnemosyne.database().con.execute(\
    """select _id, _fact_id from cards order by creation_time desc"""):
    card = mnemosyne.database().card(cursor[0], is_id_internal=True)
    if card.fact._id not in _fact_ids and text_in_tag in card.tag_string():
        count += 1
        if count == cards_to_export:
            break
        _fact_ids.append(card.fact._id )
        q = card.question(render_chain="plain_text").encode("utf-8")
        a = card.answer(render_chain="plain_text").encode("utf-8")
        # We write the answer first to have alignment in columns
        # (Arabic is not monospace).
        print(a + (40-len(a))*" " + q, file=f)
f.close()

os.system("unoconv mnemosyne.txt")

mnemosyne.finalise()
