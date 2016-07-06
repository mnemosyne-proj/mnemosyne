# Choose the correct python and virtualenv commands:

PYTHON      := python
VIRTUALENV  := virtualenv
SPHINXBUILD := sphinx-build

# If `python3` exists:
ifeq (1,$(shell python3 -c "print(1)" 2>&- ))
PYTHON      := python3
endif
# If we are on cygwin:
ifeq (1,$(shell /cygdrive/c/Program\ Files/Python35/python.exe -c "print(1)" 2>&- ))
PYTHON      := /cygdrive/c/Program\ Files/Python35/python.exe
VIRTUALENV  := /cygdrive/c/Program\ Files/Python35/Scripts/virtualenv.exe
endif
# If "--system-site-packages" supported:
ifneq (,$(shell $(VIRTUALENV) --system-site-packages --version 3>&- ))
VIRTUALENV  += --system-site-packages
endif
# If `sphinx-build2` exists:
ifneq (,$(shell command -v sphinx-build2 2>&- ))
SPHINXBUILD := sphinx-build2
endif

export PYTHON # pass the variable to sub-makefiles through the environment

# Allow specifying an alternate root destination dir for system-wide installation:

ifdef DESTDIR
INSTALL_OPTS += --root="$(DESTDIR)"
endif

install-and-run-virtual-env: install-virtual-env
	./bin/mnemosyne -d dot_mnemosyne2

install-virtual-env:
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc5 -o mnemosyne_rc.py mnemosyne.qrc
	./bin/python setup.py develop

setup:
	$(VIRTUALENV) --python=$(PYTHON) .
	./bin/pip install nose
	./bin/pip install coverage
	cd po && make

# Note: virtualenvs seem impossible at the moment: qwebengine view simly refuses
# to show content, both with and without system-site-packages and both by copying
# the directory and by using pip.
# (Moreover I cannot get numpy to compile from sounce, but that's a different issue)

setup-windows:
	#virtualenv -p python3 --system-site-packages --python=C:/Program\ Files/python35/python.exe .
	virtualenv -p python3 --no-site-packages --python=C:/Program\ Files/python35/python.exe .
	cp C:/Program\ Files/Python35/mplayer.exe Scripts/
	cp -r C:/Program\ Files/Python35/Lib/site-packages/ Lib/
	Scripts/pip.exe install pyqt5
	#cp -r C:/Program\ Files/Python35/Lib/site-packages/PyQt5/ Lib/site-packages/
	#cp C:/Program\ Files/Python35/Lib/site-packages/PyQt5/resources/* Scripts
	Scripts/pip.exe install nose
	Scripts/pip.exe install coverage

install-virtual-env-windows:
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc5 -o mnemosyne_rc.py mnemosyne.qrc
	Scripts/python.exe setup.py develop
	
	
install-system-tmp:
	cd mnemosyne/pyqt_ui && make clean
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc5 -o mnemosyne_rc.py mnemosyne.qrc
	C:/Program\ Files/python35/python.exe setup.py install $(INSTALL_OPTS)
	rm -f -R build
	

install-system:
	# Also rebuilds the docs and the translations.
	cd mnemosyne/libmnemosyne/docs && make SPHINXBUILD=$(SPHINXBUILD) html
	cd mnemosyne/pyqt_ui && make clean
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc5 -o mnemosyne_rc.py mnemosyne.qrc
	cd po && make update
	cd po && make
	$(PYTHON) setup.py install $(INSTALL_OPTS)
	rm -f -R build
	
build-all-deps:
	# Also rebuilds the docs and the translations.
	cd mnemosyne/libmnemosyne/docs && make SPHINXBUILD=$(SPHINXBUILD) html
	# cd mnemosyne/pyqt_ui && make clean
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc5 -o mnemosyne_rc.py mnemosyne.qrc
	cd po && make update
	cd po && make

test: install-virtual-env
	./bin/nosetests tests
	
test-windows:
	Scripts/nosetests.exe tests
	
coverage: install-virtual-env
	rm -rf .coverage cover htmlcov
	./bin/nosetests --with-coverage --cover-erase \
	--cover-package=mnemosyne.libmnemosyne,openSM2sync || (echo "testsuite failed")
	./bin/coverage html
	firefox htmlcov/index.html || chromium htmlcov/index.html || google-chrome htmlcov/index.html
	
coverage-windows: install-virtual-env-windows
	rm -rf .coverage cover htmlcov
	Scripts/nosetests --with-coverage --cover-erase \
	--cover-package=mnemosyne.libmnemosyne,openSM2sync || (echo "testsuite failed")
	Scripts/coverage html
	firefox htmlcov/index.html || chromium htmlcov/index.html || google-chrome htmlcov/index.html
	
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

osx: 	# Contributed by Patrick Kenny and Devin Howard
	# make sure there are no existing build files
	sudo rm -rf build/ dist/

	# build the UI and the translations
	cd mnemosyne/pyqt_ui && make clean
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc
	cd po && make

	# build the app with py2app
	sudo $(PYTHON) setup.py py2app

	# add a blank qt.conf so that the system will used the bundled qt instead of the system qt if the system already has qt installed
	sudo touch dist/Mnemosyne.app/Contents/Resources/qt.conf
	sudo cp -R /usr/local/opt/qt/lib/QtGui.framework/Versions/4/Resources/qt_menu.nib dist/Mnemosyne.app/Contents/Resources/

	# add the translations
	sudo mkdir -p dist/Mnemosyne.app/Contents/Resources/share
	sudo cp -R mo dist/Mnemosyne.app/Contents/Resources/share/locale

wm: install-virtual-env
	cp mnemosyne/ppygui_ui/ppygui_ui/*.py mnemosyne/ppygui_ui/
	./bin/python mnemosyne/ppygui_ui/Mnemosyne\ Mobile.py

docs:
	cd mnemosyne/libmnemosyne/docs && make html
	
android: # Creats the assets file with the Python code.
	rm -f mnemosyne/android/app/src/main/assets/mnemosyne.zip
	#python -m compileall mnemosyne
	zip	-r mnemosyne/android/app/src/main/assets/mnemosyne.zip openSM2sync -i \*.py
	zip -r mnemosyne/android/app/src/main/assets/mnemosyne.zip mnemosyne/libmnemosyne -i \*.py
	zip	-r mnemosyne/android/app/src/main/assets/mnemosyne.zip mnemosyne/cle -i \*.py
	zip	mnemosyne/android/app/src/main/assets/mnemosyne.zip mnemosyne/version.py mnemosyne/__init__.py	
	
windows-installer:
	rm -rf dist
	rm -rf build
	cd mnemosyne/pyqt_ui && make clean
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc
	cd po && make
	$(PYTHON) setup.py py2exe
	read -p "Press any key when InnoSetup has finished..."
	V=`$(PYTHON) mnemosyne/version.py` && cp dist/Output/setup.exe mnemosyne-$${V}-setup.exe

clean:
	rm -f *~ *.pyc *.tgz process_profile.py
	rm -rf dist
	rm -f -R Mnemosyne.egg-info
	rm -f -R distrib build bin lib Lib Scripts include dot_mnemosyne2 dot_test dot_sync_*
	rm -f -R dot_benchmark dist
	cd mnemosyne/pyqt_ui && make clean
	cd po && make clean
	rm -f mnemosyne/*~ mnemosyne/*.pyc
	rm -f mnemosyne/libmnemosyne/*~ mnemosyne/libmnemosyne/*.pyc

distrib: FORCE
	rm -rf dist
	rm -rf Mnemosyne.egg-info
	cd po && make
	cd mnemosyne/libmnemosyne/docs && make html
	cd mnemosyne/pyqt_ui && make
	$(PYTHON) setup.py sdist --formats=gztar

distrib-WM: FORCE
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
