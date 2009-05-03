#!/usr/bin/env python

import os
from mnemosyne.libmnemosyne import Mnemosyne

mnemosyne = Mnemosyne()
mnemosyne = Mnemosyne(resource_limited=True)
mnemosyne.initialise(basedir=os.path.abspath("dot_mnemosyne2"), main_widget=None,
    extra_components=[("HtmlCssOld",
    "mnemosyne.libmnemosyne.renderers.html_css_old")])

#amar-sin pc timings
#begin: .161 sec
#only import uuid when needed in fact and category: 0.122
#remove uuid import from configuration: 0.046
#with ppygui extra components, resource limite

#   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        1    0.000    0.000    0.036    0.036 {execfile}
#        1    0.000    0.000    0.036    0.036 startup_time.py:6(<module>)
#        1    0.000    0.000    0.030    0.030 __init__.py:33(initialise)
#        1    0.002    0.002    0.020    0.020 __init__.py:53(initialise_system_components)
#       63    0.000    0.000    0.013    0.000 gettext.py:580(gettext)
#       63    0.000    0.000    0.013    0.000 gettext.py:542(dgettext)
#       63    0.000    0.000    0.013    0.000 gettext.py:476(translation)
#       63    0.002    0.000    0.012    0.000 gettext.py:421(find)
#      516    0.001    0.000    0.006    0.000 genericpath.py:15(exists)
#        1    0.000    0.000    0.006    0.006 __init__.py:5(<module>)
#        1    0.000    0.000    0.005    0.005 __init__.py:183(load_database)
#        1    0.000    0.000    0.005    0.005 SQLite.py:134(load)
#        1    0.000    0.000    0.005    0.005 exceptions.py:5(<module>)
#      517    0.004    0.000    0.004    0.000 {posix.stat}
#        1    0.000    0.000    0.004    0.004 {built-in method strptime}

# Getting rid of gettext

#   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
#        1    0.000    0.000    0.023    0.023 {execfile}
#        1    0.000    0.000    0.023    0.023 startup_time.py:3(<module>)
#        1    0.000    0.000    0.022    0.022 __init__.py:27(initialise)
#        1    0.002    0.002    0.013    0.013 __init__.py:52(initialise_system_components)
#        1    0.000    0.000    0.005    0.005 __init__.py:184(load_database)
#        1    0.000    0.000    0.005    0.005 SQLite.py:134(load)
#        1    0.000    0.000    0.004    0.004 {built-in method strptime}
#       15    0.000    0.000    0.003    0.000 re.py:188(compile)
#       15    0.000    0.000    0.003    0.000 re.py:229(_compile)
