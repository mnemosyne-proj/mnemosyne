#! /usr/bin/python

import os, shutil

for filename in os.listdir("."):
    if filename.endswith("po"):
        print filename
        os.system ("msgmerge " + filename + " mnemosyne.pot -o " + filename)

