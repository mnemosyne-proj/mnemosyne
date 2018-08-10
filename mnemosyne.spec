# -*- mode: python -*-

import os, sys, shutil

block_cipher = None

datas = [("mo", "mo")]
excludes = []
binaries = []

hiddenimports = [
             'mnemosyne.version',
             'mnemosyne.libmnemosyne.card',
             'mnemosyne.libmnemosyne.card_type',
             'mnemosyne.libmnemosyne.card_type_converter',
             'mnemosyne.libmnemosyne.component',
             'mnemosyne.libmnemosyne.component_manager',
             'mnemosyne.libmnemosyne.configuration',
             'mnemosyne.libmnemosyne.controller',
             'mnemosyne.libmnemosyne.criterion',
             'mnemosyne.libmnemosyne.database',
             'mnemosyne.libmnemosyne.fact',
             'mnemosyne.libmnemosyne.fact_view',
             'mnemosyne.libmnemosyne.file_format',
             'mnemosyne.libmnemosyne.filter',
             'mnemosyne.libmnemosyne.hook',
             'mnemosyne.libmnemosyne.language',
             'mnemosyne.libmnemosyne.logger',
             'mnemosyne.libmnemosyne.log_uploader',
             'mnemosyne.libmnemosyne.plugin',
             'mnemosyne.libmnemosyne.renderer',
             'mnemosyne.libmnemosyne.render_chain',
             'mnemosyne.libmnemosyne.review_controller',
             'mnemosyne.libmnemosyne.scheduler',
             'mnemosyne.libmnemosyne.statistics_page',
             'mnemosyne.libmnemosyne.stopwatch',
             'mnemosyne.libmnemosyne.study_mode',
             'mnemosyne.libmnemosyne.sync_server',
             'mnemosyne.libmnemosyne.tag',
             'mnemosyne.libmnemosyne.tag_tree',
             'mnemosyne.libmnemosyne.translator',
             'mnemosyne.libmnemosyne.ui_component',
             'mnemosyne.libmnemosyne.utils',
             'mnemosyne.libmnemosyne.card_types.both_ways',
             'mnemosyne.libmnemosyne.card_types.cloze',
             'mnemosyne.libmnemosyne.card_types.front_to_back',
             'mnemosyne.libmnemosyne.card_types.map',
             'mnemosyne.libmnemosyne.card_types.M_sided',
             'mnemosyne.libmnemosyne.card_types.sentence',
             'mnemosyne.libmnemosyne.card_types.vocabulary',
             'mnemosyne.libmnemosyne.controllers.default_controller',
             'mnemosyne.libmnemosyne.criteria.default_criterion',
             'mnemosyne.libmnemosyne.databases.SQLite',
             'mnemosyne.libmnemosyne.databases.SQLite_criterion_applier',
             'mnemosyne.libmnemosyne.databases.SQLite_logging',
             'mnemosyne.libmnemosyne.databases.SQLite_media',
             'mnemosyne.libmnemosyne.databases.SQLite_no_pregenerated_data',
             'mnemosyne.libmnemosyne.databases.SQLite_statistics',
             'mnemosyne.libmnemosyne.databases.SQLite_sync',
             'mnemosyne.libmnemosyne.databases._apsw',
             'mnemosyne.libmnemosyne.databases._sqlite3',
             'mnemosyne.libmnemosyne.file_formats.anki2',
             'mnemosyne.libmnemosyne.file_formats.cuecard_wcu',
             'mnemosyne.libmnemosyne.file_formats.media_preprocessor',
             'mnemosyne.libmnemosyne.file_formats.mnemosyne1',
             'mnemosyne.libmnemosyne.file_formats.mnemosyne1_mem',
             'mnemosyne.libmnemosyne.file_formats.mnemosyne1_xml',
             'mnemosyne.libmnemosyne.file_formats.mnemosyne2_cards',
             'mnemosyne.libmnemosyne.file_formats.mnemosyne2_db',
             'mnemosyne.libmnemosyne.file_formats.science_log_parser',
             'mnemosyne.libmnemosyne.file_formats.smconv_XML',
             'mnemosyne.libmnemosyne.file_formats.supermemo_7_txt',
             'mnemosyne.libmnemosyne.file_formats.tsv',
             'mnemosyne.libmnemosyne.filters.escape_to_html',
             'mnemosyne.libmnemosyne.filters.escape_to_html_for_card_browser',
             'mnemosyne.libmnemosyne.filters.expand_paths',
             'mnemosyne.libmnemosyne.filters.html5_audio',
             'mnemosyne.libmnemosyne.filters.html5_video',
             'mnemosyne.libmnemosyne.filters.latex',
             'mnemosyne.libmnemosyne.filters.non_latin_font_size_increase',
             'mnemosyne.libmnemosyne.filters.RTL_handler',
             'mnemosyne.libmnemosyne.languagues.arabic',
             'mnemosyne.libmnemosyne.languagues.english',
             'mnemosyne.libmnemosyne.languagues.french',
             'mnemosyne.libmnemosyne.loggers.database_logger',
             'mnemosyne.libmnemosyne.renderers.html_css',
             'mnemosyne.libmnemosyne.renderers.html_css_card_browser',
             'mnemosyne.libmnemosyne.renderers.plain_text',
             'mnemosyne.libmnemosyne.renderers.anki_renderer',
             'mnemosyne.libmnemosyne.renderers.anki.decorator',
             'mnemosyne.libmnemosyne.renderers.anki.hooks',
             'mnemosyne.libmnemosyne.renderers.anki.lang',
             'mnemosyne.libmnemosyne.renderers.anki.utils',
             'mnemosyne.libmnemosyne.renderers.anki.template',
             'mnemosyne.libmnemosyne.renderers.anki.template.furigana',
             'mnemosyne.libmnemosyne.renderers.anki.template.hint',
             'mnemosyne.libmnemosyne.renderers.anki.template.template',
             'mnemosyne.libmnemosyne.renderers.anki.template.view',
             'mnemosyne.libmnemosyne.render_chains.card_browser_render_chain',
             'mnemosyne.libmnemosyne.render_chains.default_render_chain',
             'mnemosyne.libmnemosyne.render_chains.plain_text_chain',
             'mnemosyne.libmnemosyne.render_chains.sync_to_card_only_client',
             'mnemosyne.libmnemosyne.review_controllers.SM2_controller',
             'mnemosyne.libmnemosyne.review_controllers.SM2_controller_cramming',
             'mnemosyne.libmnemosyne.schedulers.cramming',
             'mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne',
             'mnemosyne.libmnemosyne.statistics_pages.cards_added',
             'mnemosyne.libmnemosyne.statistics_pages.cards_learned',
             'mnemosyne.libmnemosyne.statistics_pages.current_card',
             'mnemosyne.libmnemosyne.statistics_pages.easiness',
             'mnemosyne.libmnemosyne.statistics_pages.grades',
             'mnemosyne.libmnemosyne.statistics_pages.retention_score',
             'mnemosyne.libmnemosyne.statistics_pages.schedule',
             'mnemosyne.libmnemosyne.study_modes.cram_all',
             'mnemosyne.libmnemosyne.study_modes.cram_recent',
             'mnemosyne.libmnemosyne.study_modes.new_only',
             'mnemosyne.libmnemosyne.study_modes.scheduled_forgotten_new',
             'mnemosyne.libmnemosyne.translators.gettext_translator',
             'mnemosyne.libmnemosyne.translators.no_translator',
             'mnemosyne.libmnemosyne.ui_components.card_type_widget',
             'mnemosyne.libmnemosyne.ui_components.configuration_widget',
             'mnemosyne.libmnemosyne.ui_components.criterion_widget',
             'mnemosyne.libmnemosyne.ui_components.dialogs',
             'mnemosyne.libmnemosyne.ui_components.main_widget',
             'mnemosyne.libmnemosyne.ui_components.review_widget',
             'mnemosyne.libmnemosyne.ui_components.statistics_widget',
             'mnemosyne.libmnemosyne.upgrades.upgrade1',
             'mnemosyne.libmnemosyne.upgrades.upgrade2',
             'mnemosyne.pyqt_ui.about_dlg',
             'mnemosyne.pyqt_ui.activate_cards_dlg',
             'mnemosyne.pyqt_ui.add_cards_dlg',
             'mnemosyne.pyqt_ui.add_tags_dlg',
             'mnemosyne.pyqt_ui.browse_cards_dlg',
             'mnemosyne.pyqt_ui.card_set_name_dlg',
             'mnemosyne.pyqt_ui.card_set_language_list_wdgt',
             'mnemosyne.pyqt_ui.card_type_tree_wdgt',
             'mnemosyne.pyqt_ui.card_type_wdgt_generic',
             'mnemosyne.pyqt_ui.change_card_type_dlg',
             'mnemosyne.pyqt_ui.clone_card_type_dlg',
             'mnemosyne.pyqt_ui.completion_combo_box',
             'mnemosyne.pyqt_ui.compact_database_dlg',
             'mnemosyne.pyqt_ui.configuration',
             'mnemosyne.pyqt_ui.configuration_dlg',
             'mnemosyne.pyqt_ui.configuration_wdgt_card_appearance',
             'mnemosyne.pyqt_ui.configuration_wdgt_study',
             'mnemosyne.pyqt_ui.configuration_wdgt_main',
             'mnemosyne.pyqt_ui.configuration_wdgt_servers',
             'mnemosyne.pyqt_ui.convert_card_type_keys_dlg',
             'mnemosyne.pyqt_ui.criterion_wdgt_default',
             'mnemosyne.pyqt_ui.delete_unused_media_files_dlg',
             'mnemosyne.pyqt_ui.edit_card_dlg',
             'mnemosyne.pyqt_ui.edit_M_sided_card_type_dlg',
             'mnemosyne.pyqt_ui.edit_M_sided_card_template_wdgt',
             'mnemosyne.pyqt_ui.export_dlg',
             'mnemosyne.pyqt_ui.export_metadata_dlg',
             'mnemosyne.pyqt_ui.getting_started_dlg',
             'mnemosyne.pyqt_ui.import_dlg',
             'mnemosyne.pyqt_ui.main_wdgt',
             'mnemosyne.pyqt_ui.manage_card_types_dlg',
             'mnemosyne.pyqt_ui.manage_plugins_dlg',
             'mnemosyne.pyqt_ui.mnemosyne_rc',
             'mnemosyne.pyqt_ui.mplayer_audio',
             'mnemosyne.pyqt_ui.mplayer_video',
             'mnemosyne.pyqt_ui.prefill_tag_behaviour_plugin',
             'mnemosyne.pyqt_ui.preview_cards_dlg',
             'mnemosyne.pyqt_ui.pyqt_render_chain',
             'mnemosyne.pyqt_ui.qpushbutton2',
             'mnemosyne.pyqt_ui.qtextedit2',
             'mnemosyne.pyqt_ui.qt_sync_server',
             'mnemosyne.pyqt_ui.qt_translator',
             'mnemosyne.pyqt_ui.qt_web_server',
             'mnemosyne.pyqt_ui.qt_worker_thread',
             'mnemosyne.pyqt_ui.qwebengineview2',
             'mnemosyne.pyqt_ui.remove_tags_dlg',
             'mnemosyne.pyqt_ui.review_wdgt',
             'mnemosyne.pyqt_ui.review_wdgt_cramming',
             'mnemosyne.pyqt_ui.statistics_dlg',
             'mnemosyne.pyqt_ui.statistics_wdgts_plotting',
             'mnemosyne.pyqt_ui.statistics_wdgt_html',
             'mnemosyne.pyqt_ui.sync_dlg',
             'mnemosyne.pyqt_ui.tag_tree_wdgt',
             'mnemosyne.pyqt_ui.tip_after_starting_n_times',
             'mnemosyne.pyqt_ui.tip_dlg',
             'mnemosyne.pyqt_ui.ui_main_wdgt',
             'mnemosyne.web_server.jquery_mb_html5_audio',
             'mnemosyne.web_server.review_wdgt',
             'mnemosyne.web_server.simple_html5_audio',
             'mnemosyne.web_server.web_server',
             'mnemosyne.web_server.web_server_renderer',
             'mnemosyne.web_server.web_server_render_chain'
]

if sys.platform == "win32":
             datas.append(("C:\\Program Files (x86)\\mplayer.exe", "."))
             datas.append(("C:\\Program Files (x86)\\Python36-32\\Lib\\site-packages\\PyQt5\\Qt\\bin\\Qt5OpenGL.dll", "."))
             datas.append(("C:\\Program Files (x86)\\Python36-32\\Lib\\site-packages\\PyQt5\\Qt\\bin\\libEGL.dll", "."))
             datas.append(("C:\\Program Files (x86)\\Python36-32\\Lib\\site-packages\\PyQt5\\Qt\\bin\\libGLESv2.dll", "."))
             excludes = ['IPython', 'lib2to3']

if sys.platform == "darwin":
             hiddenimports.append('PyQt5.QtWebEngineCore')
             hiddenimports.append('PyQt5.QtWebEngineWidgets')
             binaries.append(('/usr/local/bin/mplayer', '.'))

datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', 'hooks.py'), 'anki'))
datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', 'lang.py'), 'anki'))
datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', 'utils.py'), 'anki'))
datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', 'decorator.py'), 'anki'))
datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', '__init__.py'), 'anki'))
datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', 'template', 'furigana.py'),
             os.path.join('anki', 'template')))
datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', 'template', 'hint.py'),
             os.path.join('anki', 'template')))
datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', 'template', 'template.py'),
             os.path.join('anki', 'template')))
datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', 'template', 'view.py'),
             os.path.join('anki', 'template')))
datas.append((os.path.join('mnemosyne', 'libmnemosyne', 'renderers', 'anki', 'template', '__init__.py'),
             os.path.join('anki', 'template')))

a = Analysis([os.path.join('mnemosyne', 'pyqt_ui', 'mnemosyne')],
             pathex=[os.getcwd()],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=excludes,
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

# http://stackoverflow.com/questions/4890159/python-excluding-modules-pyinstaller
a.binaries = a.binaries - TOC([
             ('tcl86t.dll', None, None),
             ('tk86t.dll', None, None),
             ('tcl86t.lib', None, None),
             ('tk86t.lib', None, None),
             ('tcl86tg.lib', None, None),
             ('tk86tg.lib', None, None),
             ('tclstub86.lib', None, None),
             ('tkstub86.lib', None, None)])

# Remove Tcl and Tk stuff (seems to cause troubles on some systems.)
# a.datas = [x for x in a.datas if not x[0].startswith("tcl")]
# a.datas = [x for x in a.datas if not x[0].startswith("tk")]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='Mnemosyne',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon=os.path.join('pixmaps', 'mnemosyne.ico'))

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Mnemosyne')

if sys.platform == "darwin":
  app = BUNDLE(coll,
               name='Mnemosyne.app',
               icon=os.path.join('pixmaps', 'mnemosyne.icns'),
               bundle_identifier='org.qt-project.Qt.QtWebEngineCore')
