default:
	cd mnemosyne/pyqt_ui ; make clean
	cd mnemosyne/pyqt_ui ; make
	#rm -f mnemosyne/pyqt_ui/locale/mnemosyne_XX.ts
	#rm -f mnemosyne/pyqt_ui/locale/mnemosyne*.qm
	#cd mnemosyne/pyqt_ui ; pylupdate4 mnemosyne.pro
	cd mnemosyne/pyqt_ui ; pyrcc4 -o mnemosyne_rc.py mnemosyne.qrc
	#cd mnemosyne/pyqt_ui ; lrelease mnemosyne.pro
	python setup.py install
	rm -f -R build

test:
	nosetests --with-coverage --cover-package=libmnemosyne	

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

	#mkdir distrib/memaid_superkaramba
	#cp memaid_superkaramba/memaid_superkaramba.py \
	#	distrib/memaid_superkaramba
	#cp memaid_superkaramba/memaid_superkaramba.theme \
	#	distrib/memaid_superkaramba
	#mkdir distrib/memaid_superkaramba/pixmaps
	#cp memaid_superkaramba/pixmaps/*.png \
	#	distrib/memaid_superkaramba/pixmaps 

	#mkdir distrib/memaid_superkaramba/docs	
	#cp memaid_superkaramba/docs/memaid_superkaramba.html \
	#	distrib/memaid_superkaramba/docs/
	#cp memaid_superkaramba/docs/memaid_superkaramba.png \
	#	distrib/memaid_superkaramba/docs/


FORCE:
