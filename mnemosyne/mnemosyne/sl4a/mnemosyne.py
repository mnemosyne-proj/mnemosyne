#
# mnemosyne.py <Peter.Bienstman@UGent.be>
#

# Simple review web server to be run on a mobile device which can also sync
# to a sync server running e.g. on a desktop or a different server.

# Modify the settings below to reflect your situation.
data_dir = "/sdcard/Mnemosyne/"
filename = "default.db"
sync_server = "myserver.mydomain.com"
sync_port = 8512
sync_username = ""
sync_password = ""

# Initialise Mnemosyne.
from mnemosyne.libmnemosyne import Mnemosyne
mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
mnemosyne.components = [\
         ("mnemosyne.libmnemosyne.translators.no_translator", 
          "NoTranslator"),
         ("mnemosyne.libmnemosyne.databases.SQLite",
          "SQLite"),
         ("mnemosyne.libmnemosyne.configuration",
          "Configuration"),
         ("mnemosyne.libmnemosyne.loggers.database_logger",
          "DatabaseLogger"),
         ("mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne",
          "SM2Mnemosyne"),
         ("mnemosyne.libmnemosyne.stopwatch",
          "Stopwatch"),
         ("mnemosyne.libmnemosyne.card_types.front_to_back",
          "FrontToBack"),
         ("mnemosyne.libmnemosyne.card_types.both_ways",
          "BothWays"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "Vocabulary"),
         ("mnemosyne.libmnemosyne.card_types.both_ways",
          "FrontToBackToBothWays"),
         ("mnemosyne.libmnemosyne.card_types.both_ways",
          "BothWaysToFrontToBack"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "FrontToBackToVocabulary"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "BothWaysToVocabulary"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "VocabularyToFrontToBack"),
         ("mnemosyne.libmnemosyne.card_types.vocabulary",
          "VocabularyToBothWays"),
         ("mnemosyne.libmnemosyne.render_chains.default_render_chain",
          "DefaultRenderChain"),
         ("mnemosyne.libmnemosyne.render_chains.plain_text_chain",
          "PlainTextChain"),
         ("mnemosyne.libmnemosyne.render_chains.sync_to_card_only_client",
          "SyncToCardOnlyClient"),
         ("mnemosyne.libmnemosyne.render_chains.card_browser_render_chain",
          "CardBrowserRenderChain"),
         ("mnemosyne.libmnemosyne.filters.latex",
          "CheckForUpdatedLatexFiles"),
         ("mnemosyne.libmnemosyne.filters.latex",
          "LatexFilenamesFromData"),
         ("mnemosyne.libmnemosyne.filters.latex",
          "DeleteUnusedLatexFiles"),
         ("mnemosyne.libmnemosyne.filters.latex",
          "PreprocessClozeLatex"),
         ("mnemosyne.libmnemosyne.filters.latex",
          "PostprocessQAClozeLatex"),
         ("mnemosyne.libmnemosyne.controllers.default_controller",
          "DefaultController"),
         ("mnemosyne.libmnemosyne.review_controllers.SM2_controller",
          "SM2Controller"),
         ("mnemosyne.libmnemosyne.card_types.map",
          "MapPlugin"),
         ("mnemosyne.libmnemosyne.card_types.cloze",
          "ClozePlugin"),
         ("mnemosyne.libmnemosyne.card_types.sentence",
          "SentencePlugin"),
         ("mnemosyne.libmnemosyne.criteria.default_criterion",
          "DefaultCriterion"),
         ("mnemosyne.libmnemosyne.databases.SQLite_criterion_applier",
          "DefaultCriterionApplier"),
         ("mnemosyne.libmnemosyne.plugins.cramming_plugin",
          "CrammingPlugin"),
         ("mnemosyne.libmnemosyne.statistics_pages.schedule",
          "Schedule"),
         ("mnemosyne.libmnemosyne.statistics_pages.retention_score",
          "RetentionScore"),
         ("mnemosyne.libmnemosyne.statistics_pages.cards_added",
          "CardsAdded"),
         ("mnemosyne.libmnemosyne.statistics_pages.cards_learned",
          "CardsLearned"),
         ("mnemosyne.libmnemosyne.statistics_pages.grades",
          "Grades"),
         ("mnemosyne.libmnemosyne.statistics_pages.easiness",
          "Easiness"),
         ("mnemosyne.libmnemosyne.statistics_pages.current_card",
          "CurrentCard"),
         ("main_wdgt", 
          "MainWdgt")]
mnemosyne.initialise(data_dir, filename=filename)

# Sync before starting the review server.
if mnemosyne.main_widget().show_question(\
    "Perform sync?", "Yes", "No", "") == 0:
    mnemosyne.controller().sync(sync_server, sync_port, 
        sync_username, sync_password)
    # Make sure the config gets picked up when starting a new
    # Mnemosyne instance in the web server.
    mnemosyne.config().save()

# Start review server.
mnemosyne.database().release_connection()
from mnemosyne.web_server.web_server import WebServerThread
web_server_thread = WebServerThread\
        (mnemosyne.component_manager, is_server_local=True)
web_server_thread.daemon = True
web_server_thread.start() 
if mnemosyne.main_widget().show_question(\
    "Review server started. Either let Mnemosyne start Chrome, or, if you have problems with sound, start Firefox yourself and go to 127.0.0.1:8513, otherwise click below to start Chrome.",
    "Start Chrome", "Don't start Chrome", "") == 0:
    mnemosyne.main_widget().start_native_browser()
web_server_thread.join()

# Sync again after the user has closed the program from the web server.
if mnemosyne.main_widget().show_question(\
    "Perform sync?", "Yes", "No", "") == 0:
    mnemosyne.controller().sync(sync_server, sync_port, 
        sync_username, sync_password)

mnemosyne.finalise()
