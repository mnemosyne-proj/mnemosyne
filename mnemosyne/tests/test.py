import os

from mnemosyne.libmnemosyne import initialise, finalise
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import card_type_by_id

#def setup_package():
#    print 'hi'
#    initialise("/home/pbienst/source/mnemosyne-trunk/mnemosyne-proj/mnemosyne/dot_test")


#def teardown_package():
#    finalise()


def test_add_cards():
    os.system("rm -fr dot_test")
    initialise("dot_test")
    fact_data = {"q" : "question", "a" : "answer"}
    card_type = card_type_by_id("1")
    ui_controller_main().create_new_cards(fact_data, card_type,
                                          grade=0, cat_names=["default"])

    ui_controller_main().file_save()
    finalise()

test_add_cards()
