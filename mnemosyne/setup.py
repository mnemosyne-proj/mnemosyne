import os, sys, shutil, glob

from distutils.core import Extension
from setuptools import setup

if sys.platform == "win32":
    pass
    #import py2exe
    #from py2exe.build_exe import py2exe
else:
    class py2exe:
        pass

import mnemosyne.version


class InnoScript:
    def __init__(self, name, lib_dir, dist_dir, windows_exe_files = [],
                 lib_files = [], qm_files = [],
                 version = mnemosyne.version.version):
        self.lib_dir = lib_dir
        self.dist_dir = dist_dir
        if not self.dist_dir[-1] in "\\/":
            self.dist_dir += "\\"
        self.name = name
        self.version = version
        self.windows_exe_files = [self.chop(p) for p in windows_exe_files]
        self.lib_files = [self.chop(p) for p in lib_files]

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]

    def create(self, pathname="dist\\mnemosyne.iss"):
        self.pathname = pathname
        ofi = self.file = open(pathname, "w")
        print("; WARNING: This script has been created by py2exe. "+\
                        "Changes to this script", file=ofi)
        print("; will be overwritten the next time py2exe is run!", file=ofi)
        print(r"[Setup]", file=ofi)
        print(r"AppName=%s" % self.name, file=ofi)
        print(r"AppVerName=%s %s" % (self.name, self.version), file=ofi)
        print(r"DefaultDirName={pf}\%s" % self.name, file=ofi)
        print(r"DefaultGroupName=%s" % self.name, file=ofi)
        print(file=ofi)

        print(r"[Files]", file=ofi)
        for path in self.windows_exe_files + self.lib_files:
            print(r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' \
                                    % (path, os.path.dirname(path)), file=ofi)
        print(file=ofi)

        print(r"[Icons]", file=ofi)
        path = self.windows_exe_files[0]
        print(r'Name: "{group}\%s"; Filename: "{app}\%s"' \
                            % (self.name, path), end=' ', file=ofi)
        print(' ; WorkingDir: {app}', file=ofi)
        #path = self.windows_exe_files[1]
        #print >> ofi, r'Name: "{group}\%s webserver"; Filename: "{app}\%s"' \
        #                    % (self.name, path),
        #print >> ofi, ' ; WorkingDir: {app}'
        #print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"'\
        #                    % self.name

    def compile(self):
        try:
            import ctypes
        except ImportError:
            try:
                import win32api
            except ImportError:
                import os
                os.startfile(self.pathname)
            else:
                print("Ok, using win32api.")
                win32api.ShellExecute(0,"compile", self.pathname, None, None, 0)
        else:
            print("Cool, you have ctypes installed.")
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                self.pathname, None, None, 0)
            if res < 32:
                raise RuntimeError("ShellExecute failed, error %d" % res)


class build_installer(): #py2exe):

    """This first builds the exe file(s), then creates a Windows installer.
    You need InnoSetup for it.

    """

    def run(self):
        # First, let py2exe do it's work.
        py2exe.run(self)
        lib_dir = self.lib_dir
        dist_dir = self.dist_dir
        # Create the Installer, using the files py2exe has created.
        # Hack to include web server, which does not seem to get picked up
        # automatically.
        script = InnoScript("Mnemosyne", lib_dir, dist_dir,
                            self.windows_exe_files, self.lib_files,
                            version=mnemosyne.version.version)
        script.create()
        script.compile()
        # Note: the final setup.exe will be in an Output subdirectory.

if sys.platform == "win32": # For py2exe.
    import matplotlib
    sys.path.append("C:\\Program Files\\Microsoft Visual Studio 9.0\\VC\\redist\\x86\\Microsoft.VC90.CRT")
    base_path = ""
    data_files = [("Microsoft.VC90.CRT", glob.glob(r"C:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*")),
                  ("mpl-data", glob.glob(r"C:\Program Files\Python35\Lib\site-packages\matplotlib\mpl-data\*.*")),
                  # Because matplotlibrc does not have an extension, glob does not find it (at least I think that"s why)
                  # So add it manually here:
                  ("mpl-data", [r"C:\Program Files\Python35\Lib\site-packages\matplotlib\mpl-data\matplotlibrc"]),
                  (r"mpl-data\images", glob.glob(r"C:\Program Files\Python35\Lib\site-packages\matplotlib\mpl-data\images\*.*")),
                  (r"mpl-data\fonts\ttf", glob.glob(r"C:\Program Files\Python35\Lib\site-packages\matplotlib\mpl-data\fonts\ttf\*.*")),
                  ("imageformats", glob.glob(r"C:\Program Files\Python35\Lib\site-packages\PyQt5\plugins\imageformats\*.dll")),
                  ("sqldrivers", ["C:\Program Files\Python35\Lib\site-packages\PyQt5\plugins\sqldrivers\qsqlite.dll"]),
                  ("", [r"C:\Program Files\Python35\mplayer.exe"])
                  ]
elif sys.platform == "darwin": # For py2app.
    base_path = ""
    data_files = [("", ["/usr/local/bin/mplayer"])]
else:
    base_path = os.path.join(sys.exec_prefix, "lib", "python" + sys.version[:3],
                             "site-packages","mnemosyne")
    data_files = [("share/applications", ["mnemosyne.desktop"]),
                  ("share/icons", ["pixmaps/mnemosyne.png"])]
# Translations.
if sys.platform == "win32":
    for mo in [x for x in glob.glob(os.path.join("mo", "*")) \
        if os.path.isdir(x)]:
        p, lang = os.path.split(mo)
        data_files.append((os.path.join("share", "locale",
            os.path.split(mo)[1], "LC_MESSAGES"),
            [os.path.join(mo, "LC_MESSAGES", "mnemosyne.mo")]))
    data_files.append((os.path.join("share", "qt4", "translations"),
        glob.glob(r"C:\Program Files\Python35\Lib\site-packages\PyQt5\translations\qt_*")))
else:
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
"includes": "sip,numpy,cherrypy,cPickle,md5,logging,shutil,xml.sax",
"iconfile": "pixmaps/mnemosyne.icns",
"qt_plugins": ["sqldrivers", "imageformats"],
"packages": "mnemosyne, mnemosyne.pyqt_ui, mnemosyne.libmnemosyne, \
    mnemosyne.libmnemosyne.translators, mnemosyne.libmnemosyne.card_types, \
    mnemosyne.libmnemosyne.databases, mnemosyne.libmnemosyne.file_formats, \
    mnemosyne.libmnemosyne.filters, mnemosyne.libmnemosyne.loggers, \
    mnemosyne.libmnemosyne.plugins, mnemosyne.libmnemosyne.renderers, \
    mnemosyne.libmnemosyne.render_chains, mnemosyne.libmnemosyne.schedulers, \
    mnemosyne.libmnemosyne.controllers, mnemosyne.libmnemosyne.ui_components, \
    mnemosyne.libmnemosyne.statistics_pages, \
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
            "mnemosyne.libmnemosyne.render_chains",
            "mnemosyne.libmnemosyne.schedulers",
            "mnemosyne.libmnemosyne.controllers",
            "mnemosyne.libmnemosyne.ui_components",
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

py2exe_options = {
    "unbuffered": True,
    "packages": ["mnemosyne", "numpy", "six", "sip", "xml.sax", "xml.etree"],
    "optimize": 2,
    "includes": ["numpy", "sip", "six", "xml.sax", "xml.etree", "PyQt5.QtNetwork",
                 "zmq.backend.cython"],
    "excludes": ["_gtkagg", "_tkagg", "_agg2", "_cairo", "_cocoaagg", "zmq.libzmq",
                 "_fltkagg", "_gtk", "_gtkcairo", "tcl", "Tkconstants", "Tkinter",
                 "pydoc", "doctest", "test"], #, "sqlite3"],
    "dll_excludes": ["libgdk-win32-2.0-0.dll", "libgobject-2.0-0.dll", "libzmq.pyd",
                     "tcl84.dll", "tk84.dll", "w9xpopen.exe"] #, "sqlite3.dll"]
}

setup(name = "Mnemosyne",
      version = mnemosyne.version.version,
      author = "Peter Bienstman",
      author_email = "Peter.Bienstman@UGent.be",
      packages = packages,
      package_dir = {"mnemosyne": "mnemosyne"},
      data_files = data_files,
      scripts = ["mnemosyne/pyqt_ui/mnemosyne"],
      # py2exe
      #windows = [{"script": "mnemosyne/pyqt_ui/mnemosyne",
      #            "icon_resources": [(1, "pixmaps/mnemosyne.ico")]}],
      #cmdclass = {"py2exe": build_installer},
      # py2app
      setup_requires = setup_requires,
      options = {"py2app": py2app_options, "py2exe": py2exe_options},
      app = py2app_app
)

