install-and-run-virtual-env: install-virtual-env
	./bin/mnemosyne -d dot_mnemosyne2

install-virtual-env:
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc
	./bin/python setup.py develop

setup:
	virtualenv .
	./bin/easy_install nose
	./bin/easy_install coverage

install-system:
	cd mnemosyne/pyqt_ui && make clean
	cd mnemosyne/pyqt_ui && make
	cd mnemosyne/pyqt_ui && pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc
	python setup.py install
	rm -f -R build

test: install-virtual-env
	./bin/nosetests tests

coverage: install-virtual-env
	./bin/nosetests --with-coverage --cover-erase --cover-html --cover-package=mnemosyne.libmnemosyne
	firefox cover/index.html

profile: install-virtual-env
	echo "from hotshot import stats" > process_profile.py
	echo "s = stats.load(\"stats.dat\")" >> process_profile.py
	echo "s.sort_stats(\"time\").print_stats()" >> process_profile.py
	./bin/nosetests --with-profile --profile-stats-file=stats.dat
	python process_profile.py

benchmark: install-virtual-env
	./bin/python tests/benchmark.py

wm: install-virtual-env
	./bin/python mnemosyne/ppygui_ui/ppygui_ui/Mnemosyne\ Mobile.py -d dot_mnemosyne2

docs:
	cd mnemosyne/libmnemosyne/docs && make html

windows:
	rmdir /S /Q dist
	rmdir /S /Q build
	python setup.py build
	python setup.py py2exe --packages=xml.sax --includes=sip

clean:
	rm -f *~ *.pyc *.tgz process_profile.py
	rm -f -R distrib build bin lib include dot_mnemosyne2 dot_test 
	rm -f -R dot_benchmark dist
	cd mnemosyne/pyqt_ui && make clean
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

	V=`python mnemosyne/version.py` && mv distrib mnemosyne-$${V}

	V=`python mnemosyne/version.py` && tar cvfz mnemosyne-$${V}.tgz \
		mnemosyne-$${V}/*

	V=`python mnemosyne/version.py` && rm -R mnemosyne-$${V}

	# Windows Mobile.

	mkdir distrib

	cp mnemosyne/ppygui_ui/INSTALL Mnemosyne\ Mobile.py distrib
	mkdir distrib/ppygui_ui
	cp -r mnemosyne/ppygui_ui/*.py distrib/ppygui_ui

	V=`python mnemosyne/version.py` && mv distrib mnemosyne-WM-$${V}

	V=`python mnemosyne/version.py` && tar cvfz mnemosyne-WM-$${V}.tgz \
		mnemosyne-WM-$${V}/*

	V=`python mnemosyne/version.py` && rm -R mnemosyne-WM-$${V}	


FORCE:
