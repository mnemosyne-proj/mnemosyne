# Mnemosyne: Optimized Flashcards and Research Project

Mnemosyne is:

- a free, open-source, spaced-repetition flashcard program that helps you learn as efficiently as possible.
- a research project into the nature of long-term memory.
If you like, you can help out and upload anomynous data about your learning process (this feature is off by default).

Important features include:

- Bi-directional syncing between several devices
- Clients for Windows/Mac/Linux and Android
- Flashcards with rich content (images, video, audio)
- Support for Google text-to-speech and Google translate
- Powerful card types
- Flexible card browser and card selection
- Visualization to illustrate your learning process
- Extensive plugin architecture and external scripting
- Different learning schedulers
- Webserver for review through browser (does not implement any security features so far)
- Cramming scheduler to review cards without affecting the regular scheduer
- Core library that allows you to easily create your own front-end.

You can find a more detailed explanation of the features on the [webpage](https://mnemosyne-proj.org/features), as well as the general [documentation](https://mnemosyne-proj.org/help/index.php).

If you just want to download the latest Mnemosyne release as a regular user, please see the [Download section](https://mnemosyne-proj.org/download-mnemosyne.php).
If you are interested in running and changing the latest code, please read on.

# Installation of the development version and hacking

We use the git version control system and [Github](https://www.github.com) to coordinate the development.
Please use a search engine to find out how to install git on your operating system.
If you are new to git and github, there are many tutorials available on the web.
For example, [this](https://try.github.io/) interactive tutorial. See also section [working locally with the code](#Working-locally-with-the-code) and [sharing your changes](#Sharing-your-changes) for some info about git and Github.

## About the code base
To get an overview of how all the different bits of the library fit together, see the documentation in the code at `mnemosyne/libmnemosyne/docs/build/html/index.html`.
In order to keep the code looking uniform, please following the standard Python style guides [PEP8](http://www.python.org/dev/peps/pep-0008/) and [PEP257](http://www.python.org/dev/peps/pep-0257/).

## Running the development code
You can find instructions for Windows [here](https://mnemosyne-proj.org/mnemosyne-development-under-windows).
The following instructions are valid for Linux and Mac (if you use homebrew or some other package manager).

### Runtime requirements
To start working on Mnemosyne, you need at least the following software.
- [Python](http://www.python.org) 3.5 or later
- [PyQt](https://www.riverbankcomputing.com/software/pyqt/download5) 5.6 or later, including QtWebEngineWidgets.
- [Matplotlib](http://matplotlib.org)
- [Easyinstall](http://peak.telecommunity.com/DevCenter/EasyInstall)
- [cheroot](https://pypi.python.org/pypi/Cheroot/) 5 or later
- [Webob](http://webob.org) 1.4 or later
- [Pillow](http://python-pillow.org)
- [gTTS](https://pypi.org/project/gTTS/) for Google text-to-speech
- [googletrans](https://pypi.org/project/googletrans/) for Google translate support
- For Latex support: the `latex` and `dvipng` commands must be available (e.g., `TeXLive` on Linux, `MacTeX` on Mac, and `MikTeX` on Windows).  On Arch based distributions, you'll need `texlive-core` package too.
- For building the docs: [sphinx](http://sphinx-doc.org) (If you get sphinx-related errors, try installing sphinx as root)
- For running the tests: [nose](https://nose.readthedocs.io/en/latest/)

You can either run a development version of Mnemosyne by using your system-wide Python installation, or by using a virtual environment with virtualenv.
If your distribution provides and packages all necessary libraries in a recent enough version, using the system-wide Python install is probably easier and the recommended way.

### Using the system-wide python installation
First, install all dependencies with your distribution's package manager.
Then, run `make build-all-deps`, followed by `make` from the top-level mnemosyne directory.
This will generate all the needed auxiliary files and start Mnemosyne with a separate datadir under dot_mnemosyne2.
If you want to use mnemosyne interactively from within a python shell, run python from the top-level mnemosyne directory.
You can check if the correct local version was imported by running `import mnemosyne; print(mnemosyne.__file__)`.

### Using a local python installation
If your distribution does not provide all required libraries, or if the libraries are too old, create a virtual environment in the top-level directory (`virtualenv venv`), activate it (`source venv/bin/activate`) and install all the required dependencies with `pip install`.
Then, follow the steps of the previous paragraph.

### Running the test suite
You can always run the test suite:
```
make test
```
or:
```
python3 -m nose --exe tests
```

Single tests can be run like this:
```
python3 -m nose --exe tests/<file_name>.py:<class_name>:<method_name>
```

Nose captures `stdout` by default.
Use the `-s` switch if you want to print output during the test run.

You can increase the verbosity level with the `-v` switch.

Add `--pdb` to the command line to automatically drop into the debugger on errors and failures.
If you want to drop into the debugger before a failure, edit the test and add the following code at the exact spot where you want the debugger to be started:
```
from nose.tools import set_trace; set_trace()
```

# System-wide installation from source
For testing the development version it is not necessary to do a system-wide installation.
If you want to do so anyway, here are the instructions.

## Linux
Follow the installation instructions from above (install the dependencies, get the source code - either by cloning it from github, or by downloading and extracting the `.tar.gz` archive).
Then, run the following command from within the top-level directory of the repository (which is also the location of this `README.md` file):
```
sudo python setup.py install
```

Depending on your setup, you might need to replace `python` with `python3`. To test the installation, change to any other directory and run `mnemosyne`.
For example:
```
cd ~
mnemosyne
```

If you run into the issue of non-latin characters not displaying on statistic
plots, install ttf-mscorefonts-installer and regenerate the font cache of
matplotlib.

## Mac
- Download and install Homebrew (see http://brew.sh)
- Open the Terminal.
- Make sure you are using the latest version of Homebrew:

```
brew update
```

- Install dependencies for Mnemosyne. 

```
brew install python qt mplayer
brew cask install xquartz # needed for mplayer dylibs
```

- For Mnemosyne 2.7.3, we used Python 3.7.9 and Qt 5.15. To confirm you're using the correct versions:

```
python --version
pip --version
```

- If the versions are not correct, andy ou need to edit a Homebrew dependency, you can use these commands:

```
brew uninstall <package-name>
brew edit <package-name>
# Example: replace the file with the contents of https://raw.githubusercontent.com/Homebrew/homebrew-core/e76ed3606c8008d2b8d9636a7e4e6f62cfeb6120/Formula/python3.rb and save it
brew install <package-name>
brew pin <package-name>
```

- Install the python dependencies for Mnemosyne, using a python virtual environment to isolate python dependencies. 
- Note for Mnemosyne 2.7.3, we used PyQt5 5.15 and PyInstaller 4.0

```
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install webob tornado matplotlib numpy sip pillow cheroot googletrans gtts pyopengl

# install development version of pyinstaller to ensure we get https://github.com/pyinstaller/pyinstaller/issues/5004
pip install -U https://github.com/pyinstaller/pyinstaller/archive/develop.zip

# run this command and inspect the output to confirm you're using the correct versions
pip install pyqt5 pyqtwebengine
```

 - Build it (while still using the python virtual environment):
```
make clean
make macos
```

 - Test the new application (back up your data directory first!):

```
open dist/Mnemosyne.app
```

 - Optionally drag and drop this new app to /Applications.

# Git and Github info
## Working locally with the code
If you want to hack on Mnemosyne and propose your changes for merging later ('pull request'), first create an account on, or log into, Github.
Then, [fork](https://github.com/mnemosyne-proj/mnemosyne#fork-destination-box) the project on Github.
You now have your own copy of the Mnemosyne repository on Github.

To work with the code, you need to clone your personal Mnemosyne fork on Github fork to your local machine.
It's best to setup [ssh for Github](https://help.github.com/articles/connecting-to-github-with-ssh/), but you don't have to.
Change to your working directory on the terminal and then clone your repository of Mnemosyne (in this example without ssh):
```
git clone https://github.com/<your-username>/mnemosyne.git
```

Let's also make it easy to track the official Mnemosyne repository:
```
git remote add upstream https://github.com/mnemosyne-proj/mnemosyne.git
```

It is best to create your own branches for your work:
```
git checkout -b <branch name>
```

Whenever you want, you can commit your changes:
```
git status
git add <files to add>
git commit -v
```

## Sharing your changes
At some point you may want to share your changes with everyone.
Before you do so, you should check make sure that you didn't introduce new test failures.
Then, you should check if changes were made to the original Mnemosyne repository on Github.
Your private fork on Github is not automatically updated with these changes.
You can get the most recent changes like this:
```
git fetch upstream
git checkout master
git merge upstream/master
```

If there are new changes, your repository now looks like this (each number symbolises a commit):

```
your local master branch:  ---1-2-3-4'-5'-6'-7'-8' (new changes from upstream)
                                  |
your local feature branch:        |-4-5-6 (your changes)
```

Before you push your branch, you should rebase it on master.
Rebasing takes all the changes in your branch (in the figure: 4-5-6) and tries to apply them on top of the master branch, so that we end up with a linear history:
```
your local master branch:  ---1-2-3-4'-5'-6'-7'-8' (new changes from upstream)
                                                |
your local feature branch:                      |-4-5-6 (your changes)
```

Rebase like this:
```
git checkout <branch name>
git rebase master
```

Follow the instructions (`git status` gives additional information).
Once you've successfully rebased your branch, push it to your Github account (we use `--force`, because we want to overwrite the existing branch on our private Github account):
```
git push origin --force <branch name>
```

To create a pull request for your changes, go to the Mnemosyne project page on Github and click on the pull request tab.
Click on 'New pull request' and follow the instructions.

Finally, some more background on the whole workflow can be found [here](https://www.atlassian.com/git/tutorials/comparing-workflows/forking-workflow).
