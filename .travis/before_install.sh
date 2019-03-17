#!/bin/bash

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
    HOMEBREW_NO_AUTO_UPDATE=1 brew install python3
    HOMEBREW_NO_AUTO_UPDATE=1 brew cask install basictex
    # dvipng is not part of basictex - compile it.
    # Alternative: 2.3 GB mactex package
    wget https://github.com/libgd/libgd/releases/download/gd-2.2.5/libgd-2.2.5.tar.gz
    tar xf libgd-2.2.5.tar.gz
    cd libgd-2.2.5
    ./configure
    make
    cd ../

    wget http://mirrors.ctan.org/dviware/dvipng.zip
    unzip dvipng.zip
    cd dvipng
    ./configure
    LD_LIBRARY_PATH=../libgd-2.5.5/src/.libs make
    cp dvipng ~/.local/bin
    chmod u+x ~/.local/bin/dvipng
else
    sudo apt-get -qq update && sudo apt-get install -y --no-install-recommends texlive-latex-base dvipng
fi
