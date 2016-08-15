import os, sys, shutil, glob, subprocess
from setuptools import setup, Command
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
        print("; WARNING: This script has been created automatically. "+\
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
                win32api.ShellExecute(0, "compile", self.pathname, None, None, 0)
        else:
            res = ctypes.windll.shell32.ShellExecuteA(0, "compile",
                self.pathname, None, None, 0)
            if res < 32:
                raise RuntimeError("ShellExecute failed, error %d" % res)


class build_installer(Command):

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
        subprocess.call(["pyinstaller",           
            "--hidden-import", "mnemosyne.version",
            "--hidden-import", "mnemosyne.libmnemosyne.card",
            "--hidden-import", "mnemosyne.libmnemosyne.card_type",
            "--hidden-import", "mnemosyne.libmnemosyne.card_type_converter",
            "--hidden-import", "mnemosyne.libmnemosyne.component",
            "--hidden-import", "mnemosyne.libmnemosyne.component_manager",
            "--hidden-import", "mnemosyne.libmnemosyne.configuration",
            "--hidden-import", "mnemosyne.libmnemosyne.controller",
            "--hidden-import", "mnemosyne.libmnemosyne.criterion",
            "--hidden-import", "mnemosyne.libmnemosyne.database",
            "--hidden-import", "mnemosyne.libmnemosyne.fact",
            "--hidden-import", "mnemosyne.libmnemosyne.fact_view",
            "--hidden-import", "mnemosyne.libmnemosyne.file_format",
            "--hidden-import", "mnemosyne.libmnemosyne.filter",
            "--hidden-import", "mnemosyne.libmnemosyne.hook",
            "--hidden-import", "mnemosyne.libmnemosyne.logger",
            "--hidden-import", "mnemosyne.libmnemosyne.log_uploader",
            "--hidden-import", "mnemosyne.libmnemosyne.plugin",
            "--hidden-import", "mnemosyne.libmnemosyne.renderer",
            "--hidden-import", "mnemosyne.libmnemosyne.render_chain",
            "--hidden-import", "mnemosyne.libmnemosyne.review_controller",
            "--hidden-import", "mnemosyne.libmnemosyne.scheduler",
            "--hidden-import", "mnemosyne.libmnemosyne.statistics_page",
            "--hidden-import", "mnemosyne.libmnemosyne.stopwatch",
            "--hidden-import", "mnemosyne.libmnemosyne.sync_server",
            "--hidden-import", "mnemosyne.libmnemosyne.tag",
            "--hidden-import", "mnemosyne.libmnemosyne.tag_tree",
            "--hidden-import", "mnemosyne.libmnemosyne.translator",
            "--hidden-import", "mnemosyne.libmnemosyne.ui_component",
            "--hidden-import", "mnemosyne.libmnemosyne.utils",
            "--hidden-import", "mnemosyne.libmnemosyne.card_types.both_ways",
            "--hidden-import", "mnemosyne.libmnemosyne.card_types.cloze",
            "--hidden-import", "mnemosyne.libmnemosyne.card_types.front_to_back",
            "--hidden-import", "mnemosyne.libmnemosyne.card_types.map",
            "--hidden-import", "mnemosyne.libmnemosyne.card_types.sentence",
            "--hidden-import", "mnemosyne.libmnemosyne.card_types.vocabulary",
            "--hidden-import", "mnemosyne.libmnemosyne.controllers.default_controller",
            "--hidden-import", "mnemosyne.libmnemosyne.criteria.default_criterion",
            "--hidden-import", "mnemosyne.libmnemosyne.databases.SQLite",
            "--hidden-import", "mnemosyne.libmnemosyne.databases.SQLite_criterion_applier",
            "--hidden-import", "mnemosyne.libmnemosyne.databases.SQLite_logging",
            "--hidden-import", "mnemosyne.libmnemosyne.databases.SQLite_media",
            "--hidden-import", "mnemosyne.libmnemosyne.databases.SQLite_no_pregenerated_data",
            "--hidden-import", "mnemosyne.libmnemosyne.databases.SQLite_statistics",
            "--hidden-import", "mnemosyne.libmnemosyne.databases.SQLite_sync",
            "--hidden-import", "mnemosyne.libmnemosyne.databases._apsw",
            "--hidden-import", "mnemosyne.libmnemosyne.databases._sqlite3",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.cuecard_wcu",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.media_preprocessor",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.mnemosyne1",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.mnemosyne1_mem",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.mnemosyne1_xml",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.mnemosyne2_cards",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.mnemosyne2_db",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.science_log_parser",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.smconv_XML",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.supermemo_7_txt",
            "--hidden-import", "mnemosyne.libmnemosyne.file_formats.tsv",
            "--hidden-import", "mnemosyne.libmnemosyne.filters.escape_to_html",
            "--hidden-import", "mnemosyne.libmnemosyne.filters.escape_to_html_for_card_browser",
            "--hidden-import", "mnemosyne.libmnemosyne.filters.expand_paths",
            "--hidden-import", "mnemosyne.libmnemosyne.filters.html5_audio",
            "--hidden-import", "mnemosyne.libmnemosyne.filters.html5_video",
            "--hidden-import", "mnemosyne.libmnemosyne.filters.latex",
            "--hidden-import", "mnemosyne.libmnemosyne.filters.non_latin_font_size_increase",
            "--hidden-import", "mnemosyne.libmnemosyne.filters.RTL_handler",
            "--hidden-import", "mnemosyne.libmnemosyne.loggers.database_logger",
            "--hidden-import", "mnemosyne.libmnemosyne.plugins.cramming_plugin",
            "--hidden-import", "mnemosyne.libmnemosyne.renderers.html_css",
            "--hidden-import", "mnemosyne.libmnemosyne.renderers.html_css_card_browser",
            "--hidden-import", "mnemosyne.libmnemosyne.renderers.plain_text",
            "--hidden-import", "mnemosyne.libmnemosyne.render_chains.card_browser_render_chain",
            "--hidden-import", "mnemosyne.libmnemosyne.render_chains.default_render_chain",
            "--hidden-import", "mnemosyne.libmnemosyne.render_chains.plain_text_chain",
            "--hidden-import", "mnemosyne.libmnemosyne.render_chains.sync_to_card_only_client",
            "--hidden-import", "mnemosyne.libmnemosyne.review_controllers.SM2_controller",
            "--hidden-import", "mnemosyne.libmnemosyne.review_controllers.SM2_controller_cramming",
            "--hidden-import", "mnemosyne.libmnemosyne.schedulers.cramming",
            "--hidden-import", "mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne",
            "--hidden-import", "mnemosyne.libmnemosyne.statistics_pages.cards_added",
            "--hidden-import", "mnemosyne.libmnemosyne.statistics_pages.cards_learned",
            "--hidden-import", "mnemosyne.libmnemosyne.statistics_pages.current_card",
            "--hidden-import", "mnemosyne.libmnemosyne.statistics_pages.easiness",
            "--hidden-import", "mnemosyne.libmnemosyne.statistics_pages.grades",
            "--hidden-import", "mnemosyne.libmnemosyne.statistics_pages.retention_score",
            "--hidden-import", "mnemosyne.libmnemosyne.statistics_pages.schedule",
            "--hidden-import", "mnemosyne.libmnemosyne.translators.gettext_translator",
            "--hidden-import", "mnemosyne.libmnemosyne.translators.no_translator",
            "--hidden-import", "mnemosyne.libmnemosyne.ui_components.card_type_widget",
            "--hidden-import", "mnemosyne.libmnemosyne.ui_components.configuration_widget",
            "--hidden-import", "mnemosyne.libmnemosyne.ui_components.criterion_widget",
            "--hidden-import", "mnemosyne.libmnemosyne.ui_components.dialogs",
            "--hidden-import", "mnemosyne.libmnemosyne.ui_components.headless_review_widget",
            "--hidden-import", "mnemosyne.libmnemosyne.ui_components.main_widget",
            "--hidden-import", "mnemosyne.libmnemosyne.ui_components.review_widget",
            "--hidden-import", "mnemosyne.libmnemosyne.ui_components.statistics_widget",
            "--hidden-import", "mnemosyne.libmnemosyne.upgrades.upgrade1",
            "--hidden-import", "mnemosyne.libmnemosyne.upgrades.upgrade2",
            "--hidden-import", "mnemosyne.libmnemosyne.upgrades.upgrade3",
            "--hidden-import", "mnemosyne.pyqt_ui.about_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.activate_cards_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.add_cards_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.add_tags_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.browse_cards_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.card_set_name_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.card_type_tree_wdgt",
            "--hidden-import", "mnemosyne.pyqt_ui.card_type_wdgt_generic",
            "--hidden-import", "mnemosyne.pyqt_ui.change_card_type_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.clone_card_type_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.compact_database_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.configuration",
            "--hidden-import", "mnemosyne.pyqt_ui.configuration_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.configuration_wdgt_card_appearance",
            "--hidden-import", "mnemosyne.pyqt_ui.configuration_wdgt_cramming",
            "--hidden-import", "mnemosyne.pyqt_ui.configuration_wdgt_main",
            "--hidden-import", "mnemosyne.pyqt_ui.configuration_wdgt_servers",
            "--hidden-import", "mnemosyne.pyqt_ui.convert_card_type_keys_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.criterion_wdgt_default",
            "--hidden-import", "mnemosyne.pyqt_ui.delete_unused_media_files_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.edit_card_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.export_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.export_metadata_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.getting_started_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.import_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.main_wdgt",
            "--hidden-import", "mnemosyne.pyqt_ui.manage_card_types_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.manage_plugins_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.mnemosyne_rc",
            "--hidden-import", "mnemosyne.pyqt_ui.mplayer_audio",
            "--hidden-import", "mnemosyne.pyqt_ui.mplayer_video",
            "--hidden-import", "mnemosyne.pyqt_ui.prefill_tag_behaviour_plugin",
            "--hidden-import", "mnemosyne.pyqt_ui.preview_cards_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.pyqt_render_chain",
            "--hidden-import", "mnemosyne.pyqt_ui.qpushbutton2",
            "--hidden-import", "mnemosyne.pyqt_ui.qtextedit2",
            "--hidden-import", "mnemosyne.pyqt_ui.qt_sync_server",
            "--hidden-import", "mnemosyne.pyqt_ui.qt_translator",
            "--hidden-import", "mnemosyne.pyqt_ui.qt_web_server",
            "--hidden-import", "mnemosyne.pyqt_ui.qwebengineview2",
            "--hidden-import", "mnemosyne.pyqt_ui.remove_tags_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.review_wdgt",
            "--hidden-import", "mnemosyne.pyqt_ui.review_wdgt_cramming",
            "--hidden-import", "mnemosyne.pyqt_ui.statistics_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.statistics_wdgts_plotting",
            "--hidden-import", "mnemosyne.pyqt_ui.statistics_wdgt_html",
            "--hidden-import", "mnemosyne.pyqt_ui.sync_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.tag_tree_wdgt",
            "--hidden-import", "mnemosyne.pyqt_ui.tip_after_starting_n_times",
            "--hidden-import", "mnemosyne.pyqt_ui.tip_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_about_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_activate_cards_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_add_cards_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_add_tags_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_browse_cards_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_card_set_name_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_change_card_type_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_clone_card_type_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_compact_database_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_configuration_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_configuration_wdgt_card_appearance",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_configuration_wdgt_cramming",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_configuration_wdgt_main",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_configuration_wdgt_servers",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_convert_card_type_keys_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_criterion_wdgt_default",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_delete_unused_media_files_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_edit_card_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_export_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_export_metadata_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_getting_started_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_import_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_main_wdgt",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_manage_card_types_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_manage_plugins_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_preview_cards_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_remove_tags_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_rename_card_type_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_rename_tag_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_review_wdgt",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_statistics_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_sync_dlg",
            "--hidden-import", "mnemosyne.pyqt_ui.ui_tip_dlg",
            "--hidden-import", "mnemosyne.web_server.jquery_mb_html5_audio",
            "--hidden-import", "mnemosyne.web_server.review_wdgt",
            "--hidden-import", "mnemosyne.web_server.simple_html5_audio",
            "--hidden-import", "mnemosyne.web_server.web_server",
            "--hidden-import", "mnemosyne.web_server.web_server_renderer",
            "--hidden-import", "mnemosyne.web_server.web_server_render_chain", 
            os.path.join("mnemosyne", "pyqt_ui", "mnemosyne")
        ])
        
        
        return
    
        if not sys.platform == "win32":
            return
        # Then, create installer with InnoSetup.
        self.lib_dir = lib_dir
        self.dist_dir = dist_dir
        script = InnoScript("Mnemosyne", self.lib_dir, self.dist_dir,
                            self.windows_exe_files, self.lib_files,
                            version=mnemosyne.version.version)
        script.create()
        script.compile()
        # Note: the final setup.exe will be in an Output subdirectory.

if sys.platform == "win32": # For py2exe.
    base_path = ""
    data_files = [("", [r"C:\Program files\Python3.5\mplayer.exe"])
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

setup(name = "Mnemosyne",
      version = mnemosyne.version.version,
      author = "Peter Bienstman",
      author_email = "Peter.Bienstman@UGent.be",
      packages = packages,
      package_dir = {"mnemosyne": "mnemosyne"},
      data_files = data_files,
      scripts = ["mnemosyne/pyqt_ui/mnemosyne"],
      #windows = [{"script": "mnemosyne/pyqt_ui/mnemosyne",
      #            "icon_resources": [(1, "pixmaps/mnemosyne.ico")]}],
      cmdclass = {"pyinstaller": build_installer},
      # py2app
      setup_requires = setup_requires,
      options = {"py2app": py2app_options},
      app = py2app_app      
)
