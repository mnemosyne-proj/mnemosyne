# Choose the correct python and virtualenv commands:

PYTHON      := python
SPHINXBUILD := sphinx-build

# If `python3` exists:
ifeq (1,$(shell python3 -c "print(1)" 2>&- ))
PYTHON      := python3
endif

# If we are on cygwin:
ifeq (1,$(shell /cygdrive/c/Program\ Files/Python311/python.exe -c "print(1)" 2>&- ))
PYTHON      := /cygdrive/c/Program\ Files/Python311/python.exe
PYTHON39    := /cygdrive/c/Program\ Files/Python39/python.exe
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

# build-all-deps: build build-po build-docs
build-all-deps: build build-docs

build:
	# Just the bare minimum to get things running
	make -C mnemosyne/pyqt_ui

build-po:
	make -C po update
	make -C po

build-docs:
	make -C mnemosyne/libmnemosyne/docs SPHINXBUILD=$(SPHINXBUILD) html

install-system: build-all-deps
	$(PYTHON) setup.py install $(INSTALL_OPTS)
	rm -f -R build

run: build
	# For debugging: running the code in place.
	PYTHONPATH=. $(PYTHON) mnemosyne/pyqt_ui/mnemosyne -d dot_mnemosyne2

test-prep:
	make -C po ../mo/de/LC_MESSAGES/mnemosyne.mo

test: test-prep
	$(PYTHON) -m pytest tests -ra --junitxml=test-results.xml

# https://pybit.es/articles/how-to-package-and-deploy-cli-apps/

wheel:
	rm -rf dist build
	$(PYTHON) -m build

pypi: wheel
	twine upload dist/*

coverage: test-prep
	rm -rf .coverage cover htmlcov
	$(PYTHON) -m pytest tests --with-coverage --cover-erase \
	    --cover-package=mnemosyne.libmnemosyne,openSM2sync || (echo "testsuite failed")
	coverage html
	@echo "Open file://$(PWD)/htmlcov/index.html in a browser for a nicer visualization."

coverage-windows: FORCE
	rm -rf .coverage cover htmlcov
	$(PYTHON) -m pytest tests --with-coverage --cover-erase \
	    --cover-package=mnemosyne.libmnemosyne,openSM2sync || (echo "testsuite failed")
	coverage html
	firefox htmlcov/index.html || chromium htmlcov/index.html || google-chrome htmlcov/index.html

profile: FORCE
	echo "from hotshot import stats" > process_profile.py
	echo "s = stats.load(\"stats.dat\")" >> process_profile.py
	echo "s.sort_stats(\"time\").print_stats()" >> process_profile.py
	$(PYTHON) -m pytest --with-profile --profile-stats-file=stats.dat
	$(PYTHON) process_profile.py

gui-profile: FORCE
	$(PYTHON) -m cProfile -s cumulative mnemosyne/pyqt_ui/mnemosyne | more

gui-profile-windows: FORCE
	$(PYTHON) -m cProfile -s cumulative mnemosyne/pyqt_ui/mnemosyne -d C:\\Users\\peter\\AppData\\Roaming\\Mnemosyne | more

benchmark: FORCE
	$(PYTHON) tests/benchmark.py

windows-installer: FORCE
	# Erase previous directories to make sure we're clean.
	rm -rf dist
	rm -rf build
	make build-all-deps
	$(PYTHON) setup.py build_windows_installer
	read -p "Press any key when InnoSetup has finished..."
	V=`$(PYTHON) mnemosyne/version.py` && cp dist/Mnemosyne/Output/mysetup.exe mnemosyne-$${V}-setup.exe

distrib: FORCE
	# Erase previous directories to make sure we're clean.
	rm -rf dist
	rm -rf Mnemosyne.egg-info
	make build-all-deps
	$(PYTHON) setup.py sdist --formats=gztar

macos:
	# Build the UI and the translations.
	make -C mnemosyne/pyqt_ui
	make -C po

	# Build the bundled app based on the specification file.
	QT6DIR=/usr/local/opt/qt6 pyinstaller --log-level WARN mnemosyne.spec

	# Blank qt.conf to ensure that bundled qt is used over system qt.
	touch dist/Mnemosyne.app/Contents/Resources/qt.conf

	# Add the translations.
	mkdir -p dist/Mnemosyne.app/Contents/Resources/share
	cp -R mo dist/Mnemosyne.app/Contents/Resources/share/locale
	ln -s ../Resources/share dist/Mnemosyne.app/Contents/MacOS/share

	# tkinter bug - data directories not present
	mkdir -p dist/Mnemosyne.app/Contents/MacOS/tk
	mkdir -p dist/Mnemosyne.app/Contents/MacOS/tcl

osx: macos

android: # Creates the assets file with the Python code.
	rm -f mnemosyne/android/app/src/main/assets/python/mnemosyne.zip
	zip -r mnemosyne/android/app/src/main/assets/python/mnemosyne.zip openSM2sync -i \*.py
	zip -r mnemosyne/android/app/src/main/assets/python/mnemosyne.zip mnemosyne/libmnemosyne -i \*.py
	zip -r mnemosyne/android/app/src/main/assets/python/mnemosyne.zip mnemosyne/android_python -i \*.py
	zip mnemosyne/android/app/src/main/assets/python/mnemosyne.zip mnemosyne/version.py mnemosyne/__init__.py
	$(PYTHON39) compile_zip.py mnemosyne/android/app/src/main/assets/python/mnemosyne.zip

clean:
	rm -f *~ *.pyc *.tgz process_profile.py
	rm -rf dist .coverage
	rm -f -R Mnemosyne.egg-info
	rm -f -R distrib build bin lib Lib Scripts include dot_test dot_sync_*
	rm -f -R dot_benchmark dist
	find . -type d -path ".*/__pycache__" -print0 | xargs -0 rm -rf
	make -C mnemosyne/pyqt_ui clean
	make -C po clean
	rm -f mnemosyne/*~ mnemosyne/*.pyc
	rm -f mnemosyne/libmnemosyne/*~ mnemosyne/libmnemosyne/*.pyc
	rm -f mnemosyne/android/app/src/main/assets/python/mnemosyne.zip

FORCE:
