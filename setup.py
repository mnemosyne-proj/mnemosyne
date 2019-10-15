import os, sys, shutil, glob, subprocess
from setuptools import setup, Command
import mnemosyne.version


class InnoScript:

    def __init__(self):
        self.name = "Mnemosyne"
        self.dist_dir = os.path.join("dist", "Mnemosyne")
        self.version = mnemosyne.version.version

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir)+1:]

    def create(self):
        self.pathname = os.path.join(\
            os.getcwd(), "dist", "Mnemosyne", "mnemosyne.iss")
        ofi = self.file = open(self.pathname, "w")
        print("; WARNING: This script has been created automatically. "+\
                        "Changes to this script", file=ofi)
        print("; will be overwritten the next time setup.py is run!", file=ofi)
        print(r"[Setup]", file=ofi)
        print(r"AppName=%s" % self.name, file=ofi)
        print(r"AppVerName=%s %s" % (self.name, self.version), file=ofi)
        print(r"DefaultDirName={pf}\%s" % self.name, file=ofi)
        print(r"DefaultGroupName=%s" % self.name, file=ofi)
        print(file=ofi)
        print(r"[Messages]", file=ofi)
        print(r"ConfirmUninstall=Are you really really sure you want to remove %1? Your cards will not be deleted.", file=ofi)
        print(file=ofi)
        print(r"[Files]", file=ofi)
        for root, dirnames, filenames in os.walk(self.dist_dir):
            for filename in filenames:
                path = self.chop(os.path.join(root, filename))
                print(r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' \
                      % (path, os.path.dirname(path)), file=ofi)
        print(file=ofi)

        print(r"[Icons]", file=ofi)
        path = "mnemosyne.exe"
        print(r'Name: "{group}\%s"; Filename: "{app}\%s"' \
                            % (self.name, path), end=' ', file=ofi)
        print(' ; WorkingDir: {app}', file=ofi)
        print(r'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"'
                            % self.name, file=ofi)


class build_windows_installer(Command):

    """This first builds the exe file(s), then creates a Windows installer.
    You need InnoSetup for it.

    """

    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        # First, let pyinstaller do it's work.
        subprocess.call(["pyinstaller", "mnemosyne.spec"])
        # Then, create installer with InnoSetup.
        InnoScript().create()
        subprocess.call([\
            "C:\Program Files (x86)\Inno Setup 5\Compil32.exe", "/cc",
            "dist\Mnemosyne\Mnemosyne.iss"])
        # Note: the final setup.exe will be in an Output subdirectory.


if sys.platform == "darwin": # For py2app.
    base_path = ""
    data_files = [("", ["/usr/local/bin/mplayer"])]
else:
    base_path = os.path.join(sys.exec_prefix, "lib", "python" + sys.version[:3],
                             "site-packages","mnemosyne")
    data_files = [(os.path.join(sys.exec_prefix, "share", "applications"), ["mnemosyne.desktop"]),
                  (os.path.join(sys.exec_prefix, "share", "icons"), ["pixmaps/mnemosyne.png"])]

# Translations.
if sys.platform != "win32":
    for mo in [x for x in glob.glob(os.path.join("mo", "*"))
               if os.path.isdir(x)]:
        data_files.append((os.path.join(sys.exec_prefix, "share", "locale",
            os.path.split(mo)[1], "LC_MESSAGES"),
            [os.path.join(mo, "LC_MESSAGES", "mnemosyne.mo")]))

pixmap_path = os.path.join(base_path, "pixmaps")
util_path = os.path.join(base_path, "util")
doc_path = os.path.join(base_path, "docs")
build_path = os.path.join(base_path, "build")

setup_requires = []

# py2app (OS X).

py2app_options = {
"argv_emulation": True,
"includes": "sip,numpy,cheroot,cPickle,md5,logging,shutil,xml.sax",
"iconfile": "pixmaps/mnemosyne.icns",
"qt_plugins": ["sqldrivers", "imageformats"],
"packages": "mnemosyne, mnemosyne.pyqt_ui, mnemosyne.libmnemosyne, \
    mnemosyne.libmnemosyne.translators, mnemosyne.libmnemosyne.card_types, \
    mnemosyne.libmnemosyne.databases, mnemosyne.libmnemosyne.file_formats, \
    mnemosyne.libmnemosyne.filters, mnemosyne.libmnemosyne.loggers, \
    mnemosyne.libmnemosyne.plugins, mnemosyne.libmnemosyne.renderers, \
    mnemosyne.libmnemosyne.renderers.anki, \
    mnemosyne.libmnemosyne.renderers.anki.template \
    mnemosyne.libmnemosyne.render_chains, mnemosyne.libmnemosyne.schedulers, \
    mnemosyne.libmnemosyne.controllers, mnemosyne.libmnemosyne.ui_components, \
    mnemosyne.libmnemosyne.statistics_pages, mnemosyne.libmnemosyne.study_modes, \
    mnemosyne.libmnemosyne.review_controllers, \
    mnemosyne.libmnemosyne.criteria, mnemosyne.libmnemosyne.upgrades, \
    mnemosyne.script, mnemosyne.web_server, openSM2sync, \
    openSM2sync.binary_formats, openSM2sync.text_formats" }

py2app_app = ["build/Mnemosyne.py"]
if "py2app" in sys.argv:
    setup_requires.append("py2app")
    # Create the application script.
    if not os.path.exists(build_path):
        os.mkdir(build_path)
    # Create a copy in build/ with name Mnemosyne.py, because py2app
    # needs a script that ends in .py.
    appscript = os.path.join(build_path, "Mnemosyne.py")
    source = os.path.join(base_path, "mnemosyne", "pyqt_ui", "mnemosyne")
    if os.path.exists(appscript):
        os.unlink(appscript)
    shutil.copyfile(source, appscript)

package_name = "mnemosyne"
packages = ["mnemosyne",
            "mnemosyne.pyqt_ui",
            "mnemosyne.libmnemosyne",
            "mnemosyne.libmnemosyne.translators",
            "mnemosyne.libmnemosyne.card_types",
            "mnemosyne.libmnemosyne.databases",
            "mnemosyne.libmnemosyne.file_formats",
            "mnemosyne.libmnemosyne.filters",
            "mnemosyne.libmnemosyne.loggers",
            "mnemosyne.libmnemosyne.plugins",
            "mnemosyne.libmnemosyne.renderers",
            "mnemosyne.libmnemosyne.renderers.anki",
            "mnemosyne.libmnemosyne.renderers.anki.template",
            "mnemosyne.libmnemosyne.render_chains",
            "mnemosyne.libmnemosyne.schedulers",
            "mnemosyne.libmnemosyne.controllers",
            "mnemosyne.libmnemosyne.ui_components",
            "mnemosyne.libmnemosyne.study_modes",
            "mnemosyne.libmnemosyne.statistics_pages",
            "mnemosyne.libmnemosyne.review_controllers",
            "mnemosyne.libmnemosyne.criteria",
            "mnemosyne.libmnemosyne.upgrades",
            "mnemosyne.script",
            "mnemosyne.web_server",
            "openSM2sync",
            "openSM2sync.binary_formats",
            "openSM2sync.text_formats"
            ]

setup(name = "Mnemosyne",
      version = mnemosyne.version.version,
      author = "Peter Bienstman",
      author_email = "Peter.Bienstman@UGent.be",
      packages = packages,
      package_dir = {"mnemosyne": "mnemosyne"},
      data_files = data_files,
      scripts = ["mnemosyne/pyqt_ui/mnemosyne"],
      cmdclass = {"build_windows_installer": build_windows_installer},
      # py2app
      setup_requires = setup_requires,
      options = {"py2app": py2app_options},
      app = py2app_app
)
