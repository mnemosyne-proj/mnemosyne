# Choose the correct python and virtualenv commands:

PYTHON     := python
VIRTUALENV := virtualenv

ifeq (1,$(shell python2 -c "print(1)" 2>&- )) # true if `python2` exists
  PYTHON     := python2
endif
ifneq (,$(shell virtualenv2 --version 2>&- )) # true if `virtualenv2` exists
  VIRTUALENV := virtualenv2
endif
ifneq (,$(shell $(VIRTUALENV) --system-site-packages --version 2>&- ))
                                              # true if "--system-site-packages" supported
  VIRTUALENV += --system-site-packages
endif

export PYTHON  # pass the variable to sub-makefiles through the environment


# Allow specifying an alternate root destination dir for system-wide installation:

ifdef DESTDIR
  INSTALL_OPTS += --root="$(DESTDIR)"
endif


install-and-run-virtual-env: install-virtual-env
	./bin/mnemosyne -d dot_mnemosyne2

install-virtual-env:
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc
	cd po && make
	./bin/python setup.py develop

setup:
	$(VIRTUALENV) --python=$(PYTHON) .
	./bin/easy_install nose
	./bin/easy_install coverage

install-system:
	cd mnemosyne/libmnemosyne/docs && make html
	cd mnemosyne/pyqt_ui && make clean
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc
	cd po && make
	$(PYTHON) setup.py install $(INSTALL_OPTS)
	rm -f -R build

test: install-virtual-env
	./bin/nosetests tests

coverage: install-virtual-env
	rm -rf .coverage cover htmlcov
	./bin/nosetests --with-coverage --cover-erase \
	--cover-package=mnemosyne.libmnemosyne,openSM2sync
	./bin/coverage html
	firefox htmlcov/index.html

profile: install-virtual-env
	echo "from hotshot import stats" > process_profile.py
	echo "s = stats.load(\"stats.dat\")" >> process_profile.py
	echo "s.sort_stats(\"time\").print_stats()" >> process_profile.py
	./bin/nosetests --with-profile --profile-stats-file=stats.dat
	$(PYTHON) process_profile.py

gui-profile:
	./bin/python -m cProfile -s cumulative bin/mnemosyne -d ./dot_mnemosyne2/ | more

benchmark: install-virtual-env
	./bin/python tests/benchmark.py

wm: install-virtual-env
	cp mnemosyne/ppygui_ui/ppygui_ui/*.py mnemosyne/ppygui_ui/
	./bin/python mnemosyne/ppygui_ui/Mnemosyne\ Mobile.py

docs:
	cd mnemosyne/libmnemosyne/docs && make html

windows:
	rm -rf dist
	rm -rf build
	cd mnemosyne/pyqt_ui && make clean
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc
	cd po && make
	$(PYTHON) setup.py py2exe

clean:
	rm -f *~ *.pyc *.tgz process_profile.py
	rm -f -R Mnemosyne.egg-info
	rm -f -R distrib build bin lib include dot_mnemosyne2 dot_test dot_sync_*
	rm -f -R dot_benchmark dist
	cd mnemosyne/pyqt_ui && make clean
	cd po && make clean
	rm -f mnemosyne/*~ mnemosyne/*.pyc
	rm -f mnemosyne/libmnemosyne/*~ mnemosyne/libmnemosyne/*.pyc

distrib: FORCE
	make clean

	# Unix.

	cd mnemosyne/pyqt_ui && make

	mkdir distrib
	cp setup.py README LICENSE AUTHORS ChangeLog mnemosyne.desktop distrib

	mkdir distrib/mnemosyne
	cp mnemosyne/*.py distrib/mnemosyne

	mkdir distrib/mnemosyne/libmnemosyne
	cp mnemosyne/core/*.py distrib/mnemosyne/core

	mkdir distrib/mnemosyne/pyqt_ui
	cp mnemosyne/pyqt_ui/*.py distrib/mnemosyne/pyqt_ui
	cp mnemosyne/pyqt_ui/*.ui distrib/mnemosyne/pyqt_ui
	cp mnemosyne/pyqt_ui/mnemosyne distrib/mnemosyne/pyqt_ui

	mkdir distrib/mnemosyne/pyqt_ui/locale
	cp mnemosyne/pyqt_ui/locale/*.ts distrib/mnemosyne/pyqt_ui/locale
	cp mnemosyne/pyqt_ui/locale/*.qm distrib/mnemosyne/pyqt_ui/locale

	mkdir distrib/pixmaps
	cp pixmaps/mnemosyne.png distrib/pixmaps
	cp pixmaps/mnemosyne.icns distrib/pixmaps

	mkdir distrib/plugins
	cp plugins/README plugins/*.py distrib/plugins

	V=`$(PYTHON) mnemosyne/version.py` && mv distrib mnemosyne-$${V}

	V=`$(PYTHON) mnemosyne/version.py` && tar cvfz mnemosyne-$${V}.tgz \
		mnemosyne-$${V}/*

	V=`$(PYTHON) mnemosyne/version.py` && rm -R mnemosyne-$${V}

	# Windows Mobile.

	mkdir distrib

	cp mnemosyne/ppygui_ui/INSTALL Mnemosyne\ Mobile.py distrib
	mkdir distrib/ppygui_ui
	cp -r mnemosyne/ppygui_ui/*.py distrib/ppygui_ui

	V=`$(PYTHON) mnemosyne/version.py` && mv distrib mnemosyne-WM-$${V}

	V=`$(PYTHON) mnemosyne/version.py` && tar cvfz mnemosyne-WM-$${V}.tgz \
		mnemosyne-WM-$${V}/*

	V=`$(PYTHON) mnemosyne/version.py` && rm -R mnemosyne-WM-$${V}


FORCE:
