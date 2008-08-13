default:
	cd mnemosyne/pyqt_ui ; make clean
	cd mnemosyne/pyqt_ui ; make
	cd mnemosyne/pyqt_ui ; pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc
	python setup.py install
	rm -f -R build

run-in-place:
	cd mnemosyne/pyqt_ui ; make clean
	cd mnemosyne/pyqt_ui ; make
	cd mnemosyne/pyqt_ui ; pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc

test:
	nosetests --with-coverage --with-doctest --cover-package=libmnemosyne

windows:
	rmdir /S /Q dist
	rmdir /S /Q build
	python setup.py build
	python setup.py py2exe --packages=xml.sax --includes=sip

clean:
	rm -f *~ *.pyc *.tgz
	rm -f -R distrib build
	cd mnemosyne/pyqt_ui ; make clean
	rm -f mnemosyne/*~ mnemosyne/*.pyc
	rm -f mnemosyne/core/*~ mnemosyne/core/*.pyc

distrib: FORCE
	make clean
	cd mnemosyne/pyqt_ui ; make

	mkdir distrib
	cp setup.py README LICENSE AUTHORS ChangeLog mnemosyne.desktop distrib

	mkdir distrib/mnemosyne
	cp mnemosyne/*.py distrib/mnemosyne

	mkdir distrib/mnemosyne/core
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

FORCE:
