import os, sys, shutil

from distutils.core import Extension
from setuptools import setup

if sys.platform == "win32":
    import py2exe
    from py2exe.build_exe import py2exe
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
        self.qm_files = [self.chop(p) for p in qm_files]

    def chop(self, pathname):
        assert pathname.startswith(self.dist_dir)
        return pathname[len(self.dist_dir):]

    def create(self, pathname="dist\\mnemosyne.iss"):
        self.pathname = pathname
        ofi = self.file = open(pathname, "w")
        print >> ofi, "; WARNING: This script has been created by py2exe. "+\
                        "Changes to this script"
        print >> ofi, "; will be overwritten the next time py2exe is run!"
        print >> ofi, r"[Setup]"
        print >> ofi, r"AppName=%s" % self.name
        print >> ofi, r"AppVerName=%s %s" % (self.name, self.version)
        print >> ofi, r"DefaultDirName={pf}\%s" % self.name
        print >> ofi, r"DefaultGroupName=%s" % self.name
        print >> ofi

        print >> ofi, r"[Files]"
        for path in self.windows_exe_files + self.lib_files + self.qm_files:
            print >> ofi, r'Source: "%s"; DestDir: "{app}\%s"; Flags: ignoreversion' \
                                    % (path, os.path.dirname(path))
        print >> ofi

        print >> ofi, r"[Icons]"
        for path in self.windows_exe_files:
            print >> ofi, r'Name: "{group}\%s"; Filename: "{app}\%s"' \
                            % (self.name, path),
        print >> ofi, ' ; WorkingDir: {app}'
        print >> ofi, 'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"'\
                            % self.name

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
                print "Ok, using win32api."
                win32api.ShellExecute(0,"compile", self.pathname, None, None, 0)
        else:
            print "Cool, you have ctypes installed."
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                self.pathname, None, None, 0)
            if res < 32:
                raise RuntimeError, "ShellExecute failed, error %d" % res


class build_installer(py2exe):

    """This first builds the exe file(s), then creates a Windows installer.
    You need InnoSetup for it.
    
    """

    def run(self):
        # First, let py2exe do it's work.
        py2exe.run(self)
        lib_dir = self.lib_dir
        dist_dir = self.dist_dir
        # Prepare to install translations. These need to be installed outside of
        # the zipped archive.
        join = os.path.join
        pyqt_ui_dir = join("mnemosyne", "pyqt_ui")
        locale_dir = join(pyqt_ui_dir, "locale")
        os.mkdir(join(dist_dir, "locale"))
        self.qm_files = []
        for p in os.listdir(locale_dir):
            if p.endswith(".qm"):
                 src = join(os.path.abspath(locale_dir), p)
                 dest = join(join(dist_dir, "locale"), p)
                 shutil.copy(src, dest)
                 self.qm_files.append(dest)
        # Create the Installer, using the files py2exe has created.
        script = InnoScript("Mnemosyne", lib_dir, dist_dir,
                            self.windows_exe_files, self.lib_files,
                            self.qm_files, version=mnemosyne.version.version)
        script.create()
        script.compile()
        # Note: the final setup.exe will be in an Output subdirectory.


if sys.platform == "win32": # For py2exe.
    base_path = ""
    data_files = None
elif sys.platform == "darwin": # For py2app.
    base_path = ""
    data_files = []
else:
    base_path = os.path.join(sys.exec_prefix, "lib", "python"+sys.version[:3],
                             "site-packages","mnemosyne")
    data_files = [('/usr/share/applications', ['mnemosyne.desktop']),
                  ('/usr/share/icons', ['pixmaps/mnemosyne.png'])]

pixmap_path = os.path.join(base_path, "pixmaps")
util_path = os.path.join(base_path, "util")
doc_path = os.path.join(base_path, "docs")
build_path = os.path.join(base_path, "build")

setup_requires = []

# py2app (OS X).
py2app_options = {
    'argv_emulation': True,
    'includes' : 'sip,qt,cPickle,md5,logging,shutil,xml.sax,\
                  xml.sax.drivers2.drv_pyexpat',
    'resources' : 'mnemosyne',
    'iconfile' : 'pixmaps/mnemosyne.icns'
}
py2app_app = ['build/Mnemosyne.py']
if 'py2app' in sys.argv:
    setup_requires.append('py2app')
    # Create the application script.
    if not os.path.exists(build_path):
        os.mkdir(build_path)
    # Create a copy in build/ with name Mnemosyne.py, because py2app
    # needs a script that ends in .py.
    appscript = os.path.join(build_path, 'Mnemosyne.py')
    source = os.path.join(base_path, "mnemosyne", "pyqt_ui", "mnemosyne")
    if os.path.exists(appscript):
        os.unlink(appscript)
    shutil.copyfile(source, appscript)

package_name = "mnemosyne"

setup (name = "Mnemosyne",
       version = mnemosyne.version.version,
       author = "Peter Bienstman",
       author_email = "Peter.Bienstman@UGent.be",
       packages = ["mnemosyne", "mnemosyne.pyqt_ui",
                   "mnemosyne.libmnemosyne",
                   "mnemosyne.libmnemosyne.card_types",
                   "mnemosyne.libmnemosyne.databases",
                   "mnemosyne.libmnemosyne.file_formats",
                   "mnemosyne.libmnemosyne.filters",
                   "mnemosyne.libmnemosyne.loggers",
                   "mnemosyne.libmnemosyne.plugins",
                   "mnemosyne.libmnemosyne.renderers",
                   "mnemosyne.libmnemosyne.schedulers",                 
                   "mnemosyne.libmnemosyne.controllers",
                   "mnemosyne.libmnemosyne.ui_components",
                   "mnemosyne.libmnemosyne.statistics_pages",  
                   "mnemosyne.libmnemosyne.review_controllers",
                   "mnemosyne.libmnemosyne.criteria",
                   "mnemosyne.libmnemosyne.upgrades",
                   "openSM2sync",
                   "openSM2sync.binary_formats",
                   "openSM2sync.text_formats",
                   "mnemosyne.webserver"
                   ],
       package_data = {"mnemosyne.pyqt_ui": ['locale/*.qm', 'mnemosyne.qrc'],
                       "mnemosyne": ['mnemosyne.qrc']},
       data_files = data_files,
       scripts = ['mnemosyne/pyqt_ui/mnemosyne', 'mnemosyne/webserver/mnemosyne-webserver'],
       # py2exe
       windows = [{'script':'mnemosyne/pyqt_ui/mnemosyne',
                   "icon_resources":[(1,"pixmaps/mnemosyne.ico")]}],
       cmdclass = {"py2exe": build_installer},
       # py2app
       setup_requires = setup_requires,
       options = {'py2app' : py2app_options},
       app = py2app_app
)

