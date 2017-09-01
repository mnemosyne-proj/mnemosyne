#
# mnemosyne_android.py <Peter.Bienstman@UGent.be>
#

try:
    import os

    # Initialise Mnemosyne.

    from mnemosyne.libmnemosyne import Mnemosyne
    mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)

    print(1)
    1/0

except Exception as e:
    print(e)
    import traceback
    traceback.print_exc()
    traceback.print_stack()
    print(traceback.format_stack())

mnemosyne.components = [\
         ("mnemosyne.libmnemosyne.translators.no_translator",
          "NoTranslator"),
         ("mnemosyne.libmnemosyne.databases.SQLite",
          "SQLite"),
         ("mnemosyne.cle.database_maintenance",
          "AndroidDatabaseMaintenance"),
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
         ("mnemosyne.libmnemosyne.render_chains.plain_text_chain",
          "PlainTextChain"),
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
         ("mnemosyne.libmnemosyne.study_modes.scheduled_forgotten_new",
          "ScheduledForgottenNew"),
         ("mnemosyne.libmnemosyne.study_modes.new_only",
          "NewOnly"),
         ("mnemosyne.libmnemosyne.study_modes.cram_all",
          "CramAll"),
         ("mnemosyne.libmnemosyne.study_modes.cram_recent",
          "CramRecent"),
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
         ("mnemosyne.cle.main_widget",
          "MainWdgt"),
         ("mnemosyne.cle.configuration",
          "AndroidConfiguration"),
         ("mnemosyne.cle.android_render_chain",
          "AndroidRenderChain"),
         ("mnemosyne.cle.sync_dlg",
          "SyncDlg"),
         ("mnemosyne.cle.activate_cards_dlg",
          "ActivateCardsDlg")]

mnemosyne.gui_for_component["ScheduledForgottenNew"] = [\
    ("mnemosyne.cle.review_widget",
     "ReviewWdgt")]
mnemosyne.gui_for_component["NewOnly"] = [\
    ("mnemosyne.cle.review_widget",
     "ReviewWdgt")]
mnemosyne.gui_for_component["CramAll"] = [\
    ("mnemosyne.cle.review_widget",
     "ReviewWdgt")]
mnemosyne.gui_for_component["CramRecent"] = [\
    ("mnemosyne.cle.review_widget",
     "ReviewWdgt")]

def start_mnemosyne(data_dir, filename, wrapper):
    mnemosyne.android = wrapper
    mnemosyne.initialise(data_dir=data_dir, filename=filename)
    mnemosyne.start_review()

def pause_mnemosyne():
    mnemosyne.database().save()
    mnemosyne.config().save()

def stop_mnemosyne():
    mnemosyne.finalise()
