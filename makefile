# Choose the correct python and virtualenv commands:

PYTHON      := python
SPHINXBUILD := sphinx-build

# If `python3` exists:
ifeq (1,$(shell python3 -c "print(1)" 2>&- ))
PYTHON      := python3
endif

# Note: PYTHON39 was removed from android target, now renamed as android-assets.
# If you are using these settings for coding the Android client,
# using Python3.9 is recommended instead, up until compile_zip.py
# behaves as expected in newer Python versions.
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

build-all-deps: build build-po build-docs

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

# Android

HOME_DIR := $(HOME)
PROJECT_ROOT := $(PWD)
PY_VERS := 3.9.16
LIB_VERS := 3.9

define p4a-headers
	p4a create --arch=$1 --dist-name=$1 --blacklist-requirements=android,libffi,openssl --requirements=python3==$(PY_VERS),hostpython3==$(PY_VERS) --force-build
endef

STDLIB_DEST_DIR := $(PROJECT_ROOT)/mnemosyne/android/app/src/main/assets/python
STDLIB_TEMP_DIR := $(STDLIB_DEST_DIR)/temp

REMOVE_STDLIB_FILES = \
	$(TEMP_DIR)/_pydecimal.pyc \
	$(TEMP_DIR)/pydoc.pyc \
	$(TEMP_DIR)/turtle.pyc \
	$(TEMP_DIR)/pickletools.pyc \
	$(TEMP_DIR)/pickle.pyc

REMOVE_STDLIB_DIRS = \
	$(TEMP_DIR)/unittest \
	$(TEMP_DIR)/turtledemo \
	$(TEMP_DIR)/pydoc_data \
	$(TEMP_DIR)/distutils

define trim-stdlib
	# Unzip stdlib.zip to a temporary directory
	unzip -q $(HOME_DIR)/.local/share/python-for-android/dists/$1/_python_bundle__$1/_python_bundle/stdlib.zip -d $(STDLIB_TEMP_DIR)

	# Remove files and directories
 	rm -f $(REMOVE_STDLIB_FILES)
 	rm -rf $(REMOVE_STDLIB_DIRS)

	# Rezip the contents of the temporary directory
	cd $(STDLIB_TEMP_DIR) && zip -rq $(STDLIB_DEST_DIR)/stdlib.zip .

	# Clean up the temporary directory
	rm -rf $(STDLIB_TEMP_DIR)
endef

define copy-headers
	mkdir -p $(PROJECT_ROOT)/mnemosyne/android/dependencies/python/include/$1
	cp -rf $(HOME_DIR)/.local/share/python-for-android/build/other_builds/python3/$1__ndk_target_26/python3/Include/* \
		$(PROJECT_ROOT)/mnemosyne/android/dependencies/python/include/$1

	mkdir -p $(PROJECT_ROOT)/mnemosyne/android/dependencies/python/lib/$1
	cp -rf $(HOME_DIR)/.local/share/python-for-android/dists/$1/libs/$1/libpython$(LIB_VERS).so \
		$(PROJECT_ROOT)/mnemosyne/android/dependencies/python/lib/$1
	cp -rf $(HOME_DIR)/.local/share/python-for-android/dists/$1/libs/$1/libsqlite3.so \
		$(PROJECT_ROOT)/mnemosyne/android/dependencies/python/lib/$1
endef

define trim-modules
	# Copy modules directory
	mkdir -p $(PROJECT_ROOT)/mnemosyne/android/app/src/$(subst -,_,$1)/assets/python
	cp -r $(HOME_DIR)/.local/share/python-for-android/dists/$1/_python_bundle__$1/_python_bundle/modules \
		$(PROJECT_ROOT)/mnemosyne/android/app/src/$(subst -,_,$1)/assets/python
	
	# Remove specific files
 	cd $(PROJECT_ROOT)/mnemosyne/android/app/src/$(subst -,_,$1)/assets/python/modules \
 		&& rm -f _decimal* _pickle* _testcapi* audioop* cmath*
endef

define android-assets
	rm -f mnemosyne/android/app/src/main/assets/python/mnemosyne.zip
	zip -r mnemosyne/android/app/src/main/assets/python/mnemosyne.zip openSM2sync -i \*.py
	zip -r mnemosyne/android/app/src/main/assets/python/mnemosyne.zip mnemosyne/libmnemosyne -i \*.py
	zip -r mnemosyne/android/app/src/main/assets/python/mnemosyne.zip mnemosyne/android_python -i \*.py
	zip mnemosyne/android/app/src/main/assets/python/mnemosyne.zip mnemosyne/version.py mnemosyne/__init__.py
	$(PYTHON) compile_zip.py mnemosyne/android/app/src/main/assets/python/mnemosyne.zip
endef

define android-build-dist
	$(call p4a-headers,$1)
	$(call copy-headers,$1)
	$(call trim-modules,$1)
endef

define android-build-all
	$(call android-build-dist,x86_64)
	$(call android-build-dist,arm64-v8a)
	$(call android-build-dist,x86)
	$(call android-build-dist,armeabi-v7a)
	$(call trim-stdlib,arm64-v8a)
	$(call android-assets)
endef

android-assets: # Creates the assets file with the Python code.
	$(call android-assets)

trim-stdlib:
	# The original documentation states that stdlib can be shared by all architectures.
	# This target is meant to be run after make android-single-dist.
	# Locking the stdlib build to the arm64-v8a architecture is just a precautionary measure
	# And for consistency.
	$(call android-build-dist,arm64-v8a)
	$(call trim-stdlib,arm64-v8a)

android:
	$(call android-build-all)

android-single-dist:
	$(call android-build-dist,$(arch))

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
