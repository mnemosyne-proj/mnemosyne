#TODO: clean up

from mnemosyne.libmnemosyne.component_manager import component_manager as cm
from mnemosyne.libmnemosyne.config import config as cfg

from mnemosyne.libmnemosyne.card_types.front_to_back import FrontToBack
from mnemosyne.libmnemosyne.card_types.both_ways import BothWays
from mnemosyne.libmnemosyne.card_types.three_sided import ThreeSided

t1 = FrontToBack(); cm.register("card_type", t1)
t2 = BothWays(); cm.register("card_type", t2)
t3 = ThreeSided(); cm.register("card_type", t3)


cfg.initialise("\dev\\null")
cfg["path"] = "\dev\\null"

from mnemosyne.libmnemosyne import *
#initialise_system_components()
#config.initialise(basedir)
#initialise_lockfile()
#initialise_new_empty_database()

from mnemosyne.libmnemosyne.databases.pickle import Pickle

cm.register("database", Pickle())

from mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne \
                                                   import SM2Mnemosyne

cm.register("scheduler", SM2Mnemosyne())

db = cm.get_current("database")
db.new("\dev\null")
def test_add_cards():

    data = {"q" : "question", "a" : "answer"}
    t1.create_new_cards(data, grade=0, cat_names=["default"])

    db.save("\dev\\null")


