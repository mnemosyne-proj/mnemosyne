#!/usr/bin/env python
#import time

#t0 = time.time()

import os
from mnemosyne.libmnemosyne import Mnemosyne

mnemosyne = Mnemosyne()
mnemosyne.initialise(basedir=os.path.abspath("dot_mnemosyne2"), main_widget=None)

#t1 = time.time()
#print t1-t0

#(home pc timings
#begin: .161 sec
#only import uuid when needed in fact and category: 0.122
#remove uuid import from configuration: 0.046
