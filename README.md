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
To start working on Mnemosyne, you need at least the following:

- [Python](http://www.python.org) 3.9
- argon2-cffi = "^21.3.0"
- cheroot = "^10.0.0"
- cherrypy = "^18.8.0"
- matplotlib = "^3.7.2"
- webob = "^1.8.7"
- sphinx = "^7.0.1"
- pyqt6 = "^6.5.1"
- pyqt6-webengine = "^6.5.0"
- decorator = "^5.1.1"
- gtts = "^2.3.2"
- google-trans-new = "^1.1.9"
- pytest = "^7.4.0"
- pytest-timeout = "^2.1.0"

The dependencies for the Android client are as follows:

- python-for-android = "^2023.9.16"
- sh = "1.13"
- cython = "^3.0.2"

All the necessary python dependencies are declared on the `pyproject.toml` and `requirements.txt`. Mnemosyne has support for Pyenv and Poetry tools, but if you prefer to work exclusively with pip, you can install the dependencies using the `requirements.txt` as follows:

```
pip install -r requirements.txt
```

There are also other external third-party tools involved with some parts of the Mnemosyne software:

- For Latex support: the `latex` and `dvipng` commands must be available (e.g., `TeXLive` on Linux, `MacTeX` on Mac, and `MikTeX` on Windows).  On Arch based distributions, you'll need `texlive-core` package too.
- For building the Android client, you need to also have the latest Android Studio, `openjdk-17-jdk` for working with the current build tools, and from the SDK Manager of Android Studio, install NDK Version 25 and SDK 33.

You can either run a development version of Mnemosyne by using your system-wide Python installation, or by using a virtual environment with virtualenv.
If your distribution provides and packages all necessary libraries in a recent enough version, using the system-wide Python install is probably easier and the recommended way.

### Using pyenv and poetry

You may use [Pyenv](https://github.com/pyenv/pyenv) and [Poetry](https://python-poetry.org/docs/) to develop for this project. Pyenv allows you to easily install and switch between multiple python interpreters, while Poetry is a modern tool for dependency management and virtual environment configuration.

To get started, open a terminal at the project root, and run `pyenv local`. This will tell `pyenv` to use the python version specified in the `.python-version` file.

Before activating `poetry`, make sure to run the following settings:

`poetry config virtualenvs.prefer-active-python true`

This will make sure that `poetry` will recognize the python interpreter activated by `pyenv`.

Afterwards, run `poetry shell` to activate the project virtual environment. Then run `poetry install` to install all dependencies on your virtual environment. You can now get started on coding for Mnemosyne.

If there is a need to change dependencies, you may either `poetry add <package_name>` to add a dependency and `poetry remove <package_name>` to remove one. Run the following command to update the `requirements.txt` for those prefer to download project dependencies via `pip install -r requirements.txt`.:

```
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### Using the system-wide python installation
First, install all dependencies with your distribution's package manager.
Then, run `make`, followed by `make run` from the top-level mnemosyne directory.
This will generate all the needed auxiliary files and start Mnemosyne with a separate datadir under `dot_mnemosyne2`.
If you want to use mnemosyne interactively from within a python shell, run python from the top-level mnemosyne directory.
You can check if the correct local version was imported by running `import mnemosyne; print(mnemosyne.__file__)`.

### Using a local python installation
If your distribution does not provide all required libraries, or if the libraries are too old, create a virtual environment in the top-level directory (`virtualenv venv`), activate it (`source venv/bin/activate`) and install all the required dependencies with `pip install`.
Then, follow the steps of the previous paragraph.

### Running the test suite

You can run the test suite through:

```
make test
```
or:

```
make test-prep
python3 -m pytest tests -ra --junitxml=test-results.xml
```

Both commands will display a summary of test results and a junitxml file named `test-results.xml`, which is useful if you wish to go through the results outside of the terminal, such as an xml reader. 

If you want to get a more actionable version of `test-results.xml`, you may run `./tools/convert_junitxml.py` after, which converts the test result xml into a simpler todo.txt format. Because of the way the xml is parsed, the summary count of `convert_junitxml.py` and the terminal results of pytest may not always match, but the tool is sufficient for acting on the test results in a plain text editor.

Single tests can be run like this:
```
python3 -m pytest tests/<file_name>.py::<class_name>::<method_name> 
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
- Create a CODESIGN_IDENTITY certificate as described at https://github.com/pyinstaller/pyinstaller/wiki/Recipe-OSX-Code-Signing
  - Open Applications > Utilities > Keychain Access
  - From the Keychain Access menu, choose Certificate Assistant > Create a Certificate
  - Name: something unique, I used "Devin Howard - Mnemosyne".
  - Identity Type: Self Signed Root
  - Certificate Type: Code signing
  - when you run "make macos" below, ensure you have set the CODESIGN_IDENTITY environment variable to the Name you chose above. For example, I run it like
      export CODESIGN_IDENTITY="Devin Howard - Mnemosyne"
      make clean
      make macos
  - But you might instead run
      export CODESIGN_IDENTITY="My Cool Certificate"
      make clean
      make macos
- Open the Terminal.
- Make sure you are using the latest version of Homebrew:

```
brew update
```

- Install dependencies for Mnemosyne. 

```
brew install python@3.9 qt@5 mplayer openjpeg libffi
brew install --cask xquartz # needed for mplayer dylibs
```

- For Mnemosyne 2.8, we used Python 3.9.13 and Qt 5.15.3. To confirm you're using the correct versions:

```
python3 --version
brew list --versions qt@5
```

- If the versions are not correct, and you need to edit a Homebrew dependency, you can use these commands:

```
brew uninstall <package-name>
brew edit <package-name>
# Example: replace the file with the contents of https://raw.githubusercontent.com/Homebrew/homebrew-core/e76ed3606c8008d2b8d9636a7e4e6f62cfeb6120/Formula/python3.rb and save it
brew install <package-name>
brew pin <package-name>
```

- Create a python virtual environment to isolate python dependencies from the rest of your system:

```
pip3 install virtualenv
virtualenv --python=python3 venv
source venv/bin/activate
```

From now on, your shell should have a `(venv)` at the beginning indicating you're inside the virtual environment. Ensure the copy of pip in the virtual environment is at least version 21.1.1 or later:

```
pip --version
```

If not, upgrade pip with

```
pip install --upgrade pip
```

- Install the python dependencies for Mnemosyne
- Note for Mnemosyne 2.11, we used PyQt6

```
pip install argon2-cffi cheroot googletrans gtts matplotlib numpy pillow pyopengl sip tornado webob 

# run this command and inspect the output to confirm you're using the correct versions
pip install pyqt6 pyinstaller
```

 - Build it (while still using the python virtual environment):

```
export CODESIGN_IDENTITY="Devin Howard - Mnemosyne" # see note above about CODESIGN_IDENTITY
make clean
make macos
```

 - Test the new application (back up your data directory first!):

```
open dist/Mnemosyne.app
```

 - Optionally drag and drop this new app to /Applications.

## Working with the Android app

The Mnemosyne android app relies on the python-for-android (p4a) tool to generate its needed python libraries and dependencies. However, python-for-android as well as Mnemosyne's android build commands assumes that you are working on a Linux or Ubuntu-like operating system.

Make sure that you also the latest Android Studio, `openjdk-17-jdk`, and from the SDK Manager of Android Studio, install NDK Version 25 and SDK 33. Also make sure that your virtual environment is active and all dependencies installed via `poetry install`, or that p4a is installed and you have Python3.9 as your active Python version.

Append the following to your resource file (.bashrc or .zhrc):

```sh
# Android Studio Command Line Tools
# For Mnemosyne Android
export ANDROIDSDK="$HOME/Android/Sdk" # The directory where tools is located
export ANDROIDNDK="$HOME/Android/Sdk/ndk/25.1.8937393"
export ANDROIDAPI="33"  # Target API version of your application
export NDKAPI="26"  # Minimum supported API version of your application
```

Then, simply run the following:

```sh
make android
```

The `make android` command automatically downloads and bundles the necessary headers and libraries for the android client for all the following architectures: x86_64, arm64-v8a, x86, armeabi-v7a. This should be all you need, but if you prefer to generate the dependencies for a single architecture instead, run the following commands:

```sh
make android-single-dist arch=arm64-v8a # substitute arm64-v8a with your preferred architecture
make trim-stdlib
make android-assets
```

Now, open Android Studio and click File >> Open. Navigate to your project root (where you installed your Mnemosyne project fork) then open the `mnemosyne/android` directory. Let Android Studio index your files. Upgrade your Gradle. Turn on your emulator or your physical device, then select `Build app`.

If anything goes wrong, refer to `mnemosyne/android_python/README.devel` for legacy instructions.


# Git and Github info

## Github CLI Tool

If you're planning on contributing more than one pull request using Git and Github, you might find https://hub.github.com to be a useful tool for managing your repositories, forks, pull requests, and branches.

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


