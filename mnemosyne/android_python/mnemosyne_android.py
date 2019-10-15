#
# mnemosyne_android.py <Peter.Bienstman@UGent.be>
#

import os
# Workaround for this bug:
#    https://github.com/pyinstaller/pyinstaller/issues/1113
import encodings.idna

os.environ["ANDROID"] = "true"

# Initialise Mnemosyne.
from mnemosyne.libmnemosyne import Mnemosyne
mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)


mnemosyne.components = [\
         ("mnemosyne.libmnemosyne.gui_translators.no_gui_translator",
          "NoGuiTranslator"),
         ("mnemosyne.libmnemosyne.databases.SQLite",
          "SQLite"),
         ("mnemosyne.android_python.database_maintenance",
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
         ("mnemosyne.libmnemosyne.card_types.M_sided",
          "MSided"),
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
         ("mnemosyne.android_python.main_widget",
          "MainWdgt"),
         ("mnemosyne.android_python.configuration",
          "AndroidConfiguration"),
         ("mnemosyne.android_python.android_render_chain",
          "AndroidRenderChain"),
         ("mnemosyne.android_python.sync_dlg",
          "SyncDlg"),
         ("mnemosyne.android_python.activate_cards_dlg",
          "ActivateCardsDlg")]

mnemosyne.gui_for_component["ScheduledForgottenNew"] = [\
    ("mnemosyne.android_python.review_widget",
     "ReviewWdgt")]
mnemosyne.gui_for_component["NewOnly"] = [\
    ("mnemosyne.android_python.review_widget",
     "ReviewWdgt")]
mnemosyne.gui_for_component["CramAll"] = [\
    ("mnemosyne.android_python.review_widget",
     "ReviewWdgt")]
mnemosyne.gui_for_component["CramRecent"] = [\
    ("mnemosyne.android_python.review_widget",
     "ReviewWdgt")]

def start_mnemosyne(args):
    mnemosyne.initialise(data_dir=args["data_dir"],
                         filename=args["filename"])
    mnemosyne.start_review()

def pause_mnemosyne(args):
    mnemosyne.database().save()
    mnemosyne.config().save()

def stop_mnemosyne(args):
    mnemosyne.finalise()

def controller_heartbeat(args):
    mnemosyne.controller().heartbeat(args["db_maintenance"])

def config_get(args):
    return mnemosyne.config()[args["key"]]

def config_set(args):
    mnemosyne.config()[args["key"]] = args["value"]

def config_save(args):
    mnemosyne.config().save()

def review_controller_show_answer(args):
    mnemosyne.review_controller().show_answer()

def review_controller_grade_answer(args):
    mnemosyne.review_controller().grade_answer(args["grade"])

def controller_show_sync_dialog_pre(args):
    mnemosyne.controller().show_sync_dialog_pre()

def controller_sync(args):
    mnemosyne.controller().sync(args["server"], args["port"],
                                args["username"], args["password"])

def controller_show_sync_dialog_post(args):
    mnemosyne.controller().show_sync_dialog_post()

def controller_star_current_card(args):
    mnemosyne.controller().star_current_card()

def controller_show_activate_cards_dialog_pre(args):
    mnemosyne.controller().show_activate_cards_dialog_pre()

def controller_show_activate_cards_dialog_post(args):
    mnemosyne.controller().show_activate_cards_dialog_post()

def controller_set_study_mode_with_id(args):
    study_mode =  mnemosyne.controller().study_mode_with_id(args["id"])
    mnemosyne.controller().set_study_mode(study_mode)

def controller_do_db_maintenance(args):
    mnemosyne.controller().do_db_maintenance()

def database_set_criterion_with_name(args):
    saved_set = args["saved_set"]
    for criterion in mnemosyne.database().criteria():
        if criterion.name == saved_set:
            mnemosyne.database().set_current_criterion(criterion)
            return

