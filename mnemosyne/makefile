# Choose the correct python and virtualenv commands:

PYTHON      := python
SPHINXBUILD := sphinx-build

# If `python3` exists:
ifeq (1,$(shell python3 -c "print(1)" 2>&- ))
PYTHON      := python3
endif
# If we are on cygwin:
ifeq (1,$(shell /cygdrive/c/Program\ Files\ \(x86\)/Python35-32/python.exe -c "print(1)" 2>&- ))
PYTHON      := /cygdrive/c/Program\ Files\ \(x86\)/Python35-32/python.exe
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

run: build
	# For debugging: running the code in place.
	PYTHONPATH=. $(PYTHON) mnemosyne/pyqt_ui/mnemosyne -d dot_mnemosyne2
	
build:
	# Just the bare minimum to get things running
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc5 -o mnemosyne_rc.py mnemosyne.qrc	
	
build-all-deps:
	# Also rebuilds the docs and the translations.
	cd mnemosyne/libmnemosyne/docs && make SPHINXBUILD=$(SPHINXBUILD) html
	cd mnemosyne/pyqt_ui && make clean
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc5 -o mnemosyne_rc.py mnemosyne.qrc
	cd po && make update
	cd po && make
	
install-system: build-all-deps
	$(PYTHON) setup.py install $(INSTALL_OPTS)
	rm -f -R build
	
test: FORCE
	nosetests tests
		
coverage: FORCE
	rm -rf .coverage cover htmlcov
	./bin/nosetests --with-coverage --cover-erase \
	--cover-package=mnemosyne.libmnemosyne,openSM2sync || (echo "testsuite failed")
	./bin/coverage html
	firefox htmlcov/index.html || chromium htmlcov/index.html || google-chrome htmlcov/index.html
	
coverage-windows: FORCE
	rm -rf .coverage cover htmlcov
	Scripts/nosetests --with-coverage --cover-erase \
	--cover-package=mnemosyne.libmnemosyne,openSM2sync || (echo "testsuite failed")
	Scripts/coverage html
	firefox htmlcov/index.html || chromium htmlcov/index.html || google-chrome htmlcov/index.html
	
profile: FORCE
	echo "from hotshot import stats" > process_profile.py
	echo "s = stats.load(\"stats.dat\")" >> process_profile.py
	echo "s.sort_stats(\"time\").print_stats()" >> process_profile.py
	./bin/nosetests --with-profile --profile-stats-file=stats.dat
	$(PYTHON) process_profile.py

gui-profile: FORCE
	$(PYTHON) -m cProfile -s cumulative bin/mnemosyne -d ./dot_mnemosyne2/ | more
	
gui-profile-windows: FORCE
	cp mnemosyne/pyqt_ui/mnemosyne tmp.py
	$(PYTHON) -m cProfile -s cumulative tmp.py -d C:\dot_test_2 | more

benchmark: FORCE
	$(PYTHON) tests/benchmark.py
	
windows-installer: FORCE
	# Erase previous directories to make sure we're clean.
	rm -rf dist
	rm -rf build
	#make build-all-deps
	$(PYTHON) setup.py build_windows_installer
	read -p "Press any key when InnoSetup has finished..."
	V=`$(PYTHON) mnemosyne/version.py` && cp dist/Mnemosyne/Output/setup.exe mnemosyne-$${V}-setup.exe

distrib: FORCE
	# Erase previous directories to make sure we're clean.
	rm -rf dist
	rm -rf Mnemosyne.egg-info
	make build-all-deps
	$(PYTHON) setup.py sdist --formats=gztar

osx:
	# Build the UI and the translations.
	cd mnemosyne/pyqt_ui && make
	cd po && make

	# Build the bundled app based on the specification file.
	pyinstaller mnemosyne.spec

	# Blank qt.conf to ensure that bundled qt is used over system qt.
	touch dist/Mnemosyne.app/Contents/Resources/qt.conf

	# Add the translations.
	mkdir -p dist/Mnemosyne.app/Contents/Resources/share
	cp -R mo dist/Mnemosyne.app/Contents/Resources/share/locale
	ln -s ../Resources/share dist/Mnemosyne.app/Contents/MacOS/share

	
android: # Creates the assets file with the Python code.
	rm -f mnemosyne/android/app/src/main/assets/mnemosyne.zip
	#python -m compileall mnemosyne
	zip	-r mnemosyne/android/app/src/main/assets/mnemosyne.zip openSM2sync -i \*.py
	zip -r mnemosyne/android/app/src/main/assets/mnemosyne.zip mnemosyne/libmnemosyne -i \*.py
	zip	-r mnemosyne/android/app/src/main/assets/mnemosyne.zip mnemosyne/cle -i \*.py
	zip	mnemosyne/android/app/src/main/assets/mnemosyne.zip mnemosyne/version.py mnemosyne/__init__.py	
	
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
	
FORCE:
