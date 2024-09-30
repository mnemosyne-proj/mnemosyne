#
# libmnemosyne <Peter.Bienstman@gmail.com>
#

import os
import sys
import importlib
import traceback
import warnings
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import expand_path, contract_path, \
    traceback_string
from mnemosyne.libmnemosyne.component_manager import new_component_manager, \
    register_component_manager, unregister_component_manager


class Mnemosyne(Component):

    """This class groups the functionality needed to initialise and finalise
    Mnemosyne in a typical scenario.

    See also 'how to write a new frontend' in the docs for more information
    on startup and configuration of libmnemosyne.

    """

    def __init__(self, upload_science_logs, interested_in_old_reps,
        asynchronous_database=False):

        """When 'upload_science_logs' is set to 'None', it means that its
        value is user-specified through the GUI. Explicitly setting this to
        True or False overrides the user choice.

        For mobile clients, it is recommended that you set
        'upload_science_logs' to 'False'. We need to specify this as an
        argument here, so that we can inject it on time to prevent the
        uploader thread from starting.

        'interested_in_old_reps' can be set to 'False' on a mobile client
        which does not show historical statistical data, in order to speed
        up the initial sync and save disk space. We've specified this as a
        non-default argument here, in order to force front-end writers to
        consider it.

        Setting 'asynchronous_database' to True increases the risk of data
        loss and should only be done to speed up the test suite.

        """

        sys.excepthook = self.handle_exception
        self.upload_science_logs = upload_science_logs
        self.interested_in_old_reps = interested_in_old_reps
        self.asynchronous_database = asynchronous_database
        self.component_manager = new_component_manager()
        self.components = [
         ("mnemosyne.libmnemosyne.databases.SQLite",
          "SQLite"),
         ("mnemosyne.libmnemosyne.database",
          "DatabaseMaintenance"),
         ("mnemosyne.libmnemosyne.configuration",
          "Configuration"),
         ("mnemosyne.libmnemosyne.loggers.database_logger",
          "DatabaseLogger"),
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
         ("mnemosyne.libmnemosyne.file_formats.mnemosyne1_mem",
          "Mnemosyne1Mem"),
         ("mnemosyne.libmnemosyne.file_formats.mnemosyne1_xml",
          "Mnemosyne1XML"),
         ("mnemosyne.libmnemosyne.file_formats.mnemosyne2_cards",
          "Mnemosyne2Cards"),
         ("mnemosyne.libmnemosyne.file_formats.mnemosyne2_db",
          "Mnemosyne2Db"),
         ("mnemosyne.libmnemosyne.file_formats.tsv",
          "Tsv"),
         ("mnemosyne.libmnemosyne.file_formats.anki2",
          "Anki2"),
         ("mnemosyne.libmnemosyne.file_formats.supermemo_7_txt",
          "SuperMemo7Txt"),
         ("mnemosyne.libmnemosyne.file_formats.smconv_XML",
          "Smconv_XML"),
         ("mnemosyne.libmnemosyne.file_formats.cuecard_wcu",
          "CuecardWcu"),
         ("mnemosyne.libmnemosyne.translator",
          "Translator"),
         ("mnemosyne.libmnemosyne.pronouncer",
          "Pronouncer"),
         ("mnemosyne.libmnemosyne.languages.afrikaans",
          "Afrikaans"),
         ("mnemosyne.libmnemosyne.languages.albanian",
          "Albanian"),
         ("mnemosyne.libmnemosyne.languages.amharic",
          "Amharic"),
         ("mnemosyne.libmnemosyne.languages.arabic",
          "Arabic"),
         ("mnemosyne.libmnemosyne.languages.armenian",
          "Armenian"),
         ("mnemosyne.libmnemosyne.languages.azerbaijani",
          "Azerbaijani"),
         ("mnemosyne.libmnemosyne.languages.basque",
          "Basque"),
         ("mnemosyne.libmnemosyne.languages.belarusian",
          "Belarusian"),
         ("mnemosyne.libmnemosyne.languages.bengali",
          "Bengali"),
         ("mnemosyne.libmnemosyne.languages.bosnian",
          "Bosnian"),
         ("mnemosyne.libmnemosyne.languages.bulgarian",
          "Bulgarian"),
         ("mnemosyne.libmnemosyne.languages.catalan",
          "Catalan"),
         ("mnemosyne.libmnemosyne.languages.cebuano",
          "Cebuano"),
         ("mnemosyne.libmnemosyne.languages.chinese",
          "Chinese"),
         ("mnemosyne.libmnemosyne.languages.corsican",
          "Corsican"),
         ("mnemosyne.libmnemosyne.languages.croatian",
          "Croatian"),
         ("mnemosyne.libmnemosyne.languages.czech",
          "Czech"),
         ("mnemosyne.libmnemosyne.languages.danish",
          "Danish"),
         ("mnemosyne.libmnemosyne.languages.dutch",
          "Dutch"),
         ("mnemosyne.libmnemosyne.languages.english",
          "English"),
         ("mnemosyne.libmnemosyne.languages.esperanto",
          "Esperanto"),
         ("mnemosyne.libmnemosyne.languages.estonian",
          "Estonian"),
         ("mnemosyne.libmnemosyne.languages.finnish",
          "Finnish"),
         ("mnemosyne.libmnemosyne.languages.french",
          "French"),
         ("mnemosyne.libmnemosyne.languages.frisian",
          "Frisian"),
         ("mnemosyne.libmnemosyne.languages.gaelic",
          "Gaelic"),
         ("mnemosyne.libmnemosyne.languages.galician",
          "Galician"),
         ("mnemosyne.libmnemosyne.languages.georgian",
          "Georgian"),
         ("mnemosyne.libmnemosyne.languages.german",
          "German"),
         ("mnemosyne.libmnemosyne.languages.greek",
          "Greek"),
         ("mnemosyne.libmnemosyne.languages.gujarati",
          "Gujarati"),
         ("mnemosyne.libmnemosyne.languages.haitian",
          "Haitian"),
         ("mnemosyne.libmnemosyne.languages.hausa",
          "Hausa"),
         ("mnemosyne.libmnemosyne.languages.hawaiian",
          "Hawaiian"),
         ("mnemosyne.libmnemosyne.languages.hebrew",
          "Hebrew"),
         ("mnemosyne.libmnemosyne.languages.hindi",
          "Hindi"),
         ("mnemosyne.libmnemosyne.languages.hmong",
          "Hmong"),
         ("mnemosyne.libmnemosyne.languages.hungarian",
          "Hungarian"),
         ("mnemosyne.libmnemosyne.languages.icelandic",
          "Icelandic"),
         ("mnemosyne.libmnemosyne.languages.igbo",
          "Igbo"),
         ("mnemosyne.libmnemosyne.languages.indonesian",
          "Indonesian"),
         ("mnemosyne.libmnemosyne.languages.irish",
          "Irish"),
         ("mnemosyne.libmnemosyne.languages.italian",
          "Italian"),
         ("mnemosyne.libmnemosyne.languages.japanese",
          "Japanese"),
         ("mnemosyne.libmnemosyne.languages.javanese",
          "Javanese"),
         ("mnemosyne.libmnemosyne.languages.kannada",
          "Kannada"),
         ("mnemosyne.libmnemosyne.languages.kazakh",
          "Kazakh"),
         ("mnemosyne.libmnemosyne.languages.khmer",
          "Khmer"),
         ("mnemosyne.libmnemosyne.languages.korean",
          "Korean"),
         ("mnemosyne.libmnemosyne.languages.kurdish",
          "Kurdish"),
         ("mnemosyne.libmnemosyne.languages.kyrgyz",
          "Kyrgyz"),
         ("mnemosyne.libmnemosyne.languages.lao",
          "Lao"),
         ("mnemosyne.libmnemosyne.languages.latin",
          "Latin"),
         ("mnemosyne.libmnemosyne.languages.latvian",
          "Latvian"),
         ("mnemosyne.libmnemosyne.languages.lithuanian",
          "Lithuanian"),
         ("mnemosyne.libmnemosyne.languages.luxembourgish",
          "Luxembourgish"),
         ("mnemosyne.libmnemosyne.languages.macedonian",
          "Macedonian"),
         ("mnemosyne.libmnemosyne.languages.malagasy",
          "Malagasy"),
         ("mnemosyne.libmnemosyne.languages.malay",
          "Malay"),
         ("mnemosyne.libmnemosyne.languages.malayalam",
          "Malayalam"),
         ("mnemosyne.libmnemosyne.languages.maltese",
          "Maltese"),
         ("mnemosyne.libmnemosyne.languages.maori",
          "Maori"),
         ("mnemosyne.libmnemosyne.languages.marathi",
          "Marathi"),
         ("mnemosyne.libmnemosyne.languages.mongolian",
          "Mongolian"),
         ("mnemosyne.libmnemosyne.languages.myanmar",
          "Myanmar"),
         ("mnemosyne.libmnemosyne.languages.nepali",
          "Nepali"),
         ("mnemosyne.libmnemosyne.languages.norwegian",
          "Norwegian"),
         ("mnemosyne.libmnemosyne.languages.nyanja",
          "Nyanja"),
         ("mnemosyne.libmnemosyne.languages.pashto",
          "Pashto"),
         ("mnemosyne.libmnemosyne.languages.persian",
          "Persian"),
         ("mnemosyne.libmnemosyne.languages.polish",
          "Polish"),
         ("mnemosyne.libmnemosyne.languages.portuguese",
          "Portuguese"),
         ("mnemosyne.libmnemosyne.languages.punjabi",
          "Punjabi"),
         ("mnemosyne.libmnemosyne.languages.romanian",
          "Romanian"),
         ("mnemosyne.libmnemosyne.languages.russian",
          "Russian"),
         ("mnemosyne.libmnemosyne.languages.samoan",
          "Samoan"),
         ("mnemosyne.libmnemosyne.languages.serbian",
          "Serbian"),
         ("mnemosyne.libmnemosyne.languages.sesotho",
          "Sesotho"),
         ("mnemosyne.libmnemosyne.languages.shona",
          "Shona"),
         ("mnemosyne.libmnemosyne.languages.sindhi",
          "Sindhi"),
         ("mnemosyne.libmnemosyne.languages.sinhala",
          "Sinhala"),
         ("mnemosyne.libmnemosyne.languages.slovak",
          "Slovak"),
         ("mnemosyne.libmnemosyne.languages.slovenian",
          "Slovenian"),
         ("mnemosyne.libmnemosyne.languages.somali",
          "Somali"),
         ("mnemosyne.libmnemosyne.languages.spanish",
          "Spanish"),
         ("mnemosyne.libmnemosyne.languages.sundanese",
          "Sundanese"),
         ("mnemosyne.libmnemosyne.languages.swahili",
          "Swahili"),
         ("mnemosyne.libmnemosyne.languages.swedish",
          "Swedish"),
         ("mnemosyne.libmnemosyne.languages.tagalog",
          "Tagalog"),
         ("mnemosyne.libmnemosyne.languages.tajik",
          "Tajik"),
         ("mnemosyne.libmnemosyne.languages.tamil",
          "Tamil"),
         ("mnemosyne.libmnemosyne.languages.telugu",
          "Telugu"),
         ("mnemosyne.libmnemosyne.languages.thai",
          "Thai"),
         ("mnemosyne.libmnemosyne.languages.turkish",
          "Turkish"),
         ("mnemosyne.libmnemosyne.languages.ukrainian",
          "Ukrainian"),
         ("mnemosyne.libmnemosyne.languages.urdu",
          "Urdu"),
         ("mnemosyne.libmnemosyne.languages.uzbek",
          "Uzbek"),
         ("mnemosyne.libmnemosyne.languages.vietnamese",
          "Vietnamese"),
         ("mnemosyne.libmnemosyne.languages.welsh",
          "Welsh"),
         ("mnemosyne.libmnemosyne.languages.xhosa",
          "Xhosa"),
         ("mnemosyne.libmnemosyne.languages.yiddish",
          "Yiddish"),
         ("mnemosyne.libmnemosyne.languages.yoruba",
          "Yoruba"),
         ("mnemosyne.libmnemosyne.languages.zulu",
          "Zulu")]
        try: # On Android, importlib.util doesn't get found, even though it's present...
            if (importlib.util.find_spec("gtts")) is not None:
                self.components.append(\
                    ("mnemosyne.libmnemosyne.pronouncers.google_pronouncer",
                    "GooglePronouncer"))
            else:
                warnings.warn("gTTS package is not installed. Text to speak feature will not be available.")
            if ((importlib.util.find_spec("google_trans_new")) is not None):
                self.components.append(\
                    ("mnemosyne.libmnemosyne.translators.google_translator", "GoogleTranslator"))
            else:
                warnings.warn("google_trans_new package is not installed. Google translate feature will not be available.")
        except:
            pass
        self.gui_for_component = {}

    def handle_exception(self, type, value, tb):
        body = "An unexpected error has occurred.\n" + \
            "Please forward the following info to the developers:\n\n" + \
            "Traceback (innermost last):\n"
        list = traceback.format_tb(tb, limit=None) + \
               traceback.format_exception_only(type, value)
        body = body + "%-20s %s" % ("".join(list[:-1]), list[-1])
        print("Log body:\n", body)
        try:
            if sys.platform != "win32":
                sys.stderr.write(body)
            if type is KeyboardInterrupt:
                self.main_widget().handle_keyboard_interrupt(body)
            else:
                self.main_widget().show_error(body)
        except:
            sys.stderr.write(body)

    def initialise(self, data_dir=None, config_dir=None,
                   filename=None, automatic_upgrades=True, debug_file=None,
                   server_only=False):

        """The automatic upgrades of the database can be turned off by setting
        'automatic_upgrade' to False. This is mainly useful for the testsuite.

        """

        if debug_file:
            self.component_manager.debug_file = open(debug_file, "w")
        self.register_components()
        # Upgrade from 1.x if needed.
        if automatic_upgrades:
            from mnemosyne.libmnemosyne.upgrades.upgrade1 import Upgrade1
            Upgrade1(self.component_manager).backup_old_dir()
        if data_dir:
            self.config().data_dir = data_dir
            self.config().config_dir = data_dir
        if config_dir:
            self.config().config_dir = config_dir
        self.activate_components()
        register_component_manager(self.component_manager,
                                   self.config()["user_id"])
        self.execute_user_plugin_dir()
        self.activate_saved_plugins()
        # If we are only running a sync or a review server, do not yet load
        # the database to prevent threading access issues.
        if server_only:
            if filename:
                self.config()["last_database"] = \
                    contract_path(filename, self.config().data_dir)
            return
        # Loading the database should come after all user plugins have been
        # loaded, since these could be needed e.g. for a card type in the
        # database.
        if filename and not filename.endswith(".db"):
            from mnemosyne.libmnemosyne.gui_translator import _
            self.main_widget().show_error(\
                _("Command line argument is not a *.db file."))
            sys.exit()
        self.load_database(filename)
        # Only now that the database is loaded, we can start writing log
        # events to it. This is why we log started_scheduler and
        # loaded_database manually.
        try:
            self.log().started_program()
        except Exception as e:
            if "lock" in str(e):
                from mnemosyne.libmnemosyne.gui_translator import _
                self.main_widget().show_error(\
                 _("Another copy of Mnemosyne is still running.") + "\n" + \
                 _("Continuing is impossible and will lead to data loss!"))
                sys.exit()
            else:
                raise e
        # Upgrade from 1.x if needed.
        if automatic_upgrades:
            from mnemosyne.libmnemosyne.upgrades.upgrade1 import Upgrade1
            Upgrade1(self.component_manager).run()
        # Finally, we can start the main widget and the review.
        self.main_widget().activate()
        self.start_review()

    def register_components(self):

        """We register all components, but don't activate them yet, because in
        order to activate certain components, certain other components already
        need to be registered. Also, the activation needs to happen in a
        predefined order, and we don't want to burden UI writers with listing
        the components in the correct order.

        """

        for module_name, class_name in self.components:
            component = getattr(\
                importlib.import_module(module_name), class_name)
            if component.instantiate == Component.IMMEDIATELY:
                component = component(component_manager=self.component_manager)
            self.component_manager.register(component)
        for component_name in self.gui_for_component:
            for gui_module_name, gui_class_name in \
                    self.gui_for_component[component_name]:
                gui_class = getattr(\
                    importlib.import_module(gui_module_name), gui_class_name)
                self.component_manager.add_gui_to_component(\
                    component_name, gui_class)

    def activate_components(self):

        """Now that everything is registered, we can activate the components
        in the correct order: first config, followed by log and then the rest.

        """

        # Activate config and inject necessary settings.
        try:
            self.component_manager.current("config").activate()
        except RuntimeError as e:
            self.main_widget().show_error(str(e))
        # Allow front end programmer to override the user setting.
        if self.upload_science_logs is False:
            self.config()["upload_science_logs"] = False
        if self.upload_science_logs is True:
            self.config()["upload_science_logs"] = True
        self.config()["interested_in_old_reps"] = self.interested_in_old_reps
        self.config()["asynchronous_database"] = self.asynchronous_database
        # Activate other components.
        for component in ["log", "gui_translator", "database", "controller"]:
            try:
                self.component_manager.current(component).activate()
            except RuntimeError as e:
                self.main_widget().show_error(str(e))
        sync_server = self.component_manager.current("sync_server")
        if sync_server:
            sync_server.activate()
        web_server = self.component_manager.current("web_server")
        if web_server:
            web_server.activate()

    def execute_user_plugin_dir(self):
        # Note that we put user plugins in the data_dir and not the
        # config_dir as there could be plugins (e.g. new card types) for
        # which the database does not make sense without them.
        plugin_dir = os.path.join(self.config().data_dir, "plugins")
        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)
        for component in os.listdir(plugin_dir):
            if component.endswith(".py"):
                try:
                    __import__(component[:-3])
                except:
                    from mnemosyne.libmnemosyne.gui_translator import _
                    msg = _("Error when running plugin:") \
                          + "\n" + traceback_string()
                    self.main_widget().show_error(msg)

    def activate_saved_plugins(self):
        for plugin in self.config()["active_plugins"]:
            try:
                for p in self.plugins():
                    if plugin == p.__class__.__name__:
                        p.activate()
                        break
            except:
                from mnemosyne.libmnemosyne.gui_translator import _
                msg = _("Error when running plugin:") \
                      + "\n" + traceback_string()
                self.main_widget().show_error(msg)

    def load_database(self, filename):
        if not filename:
            filename = self.config()["last_database"]
        path = expand_path(filename, self.config().data_dir)
        try:
            if not os.path.exists(path):
                try:
                    self.database().new(path)
                except Exception as e:
                    from mnemosyne.libmnemosyne.gui_translator import _
                    raise RuntimeError(\
                        _("Previous drive letter no longer available."))
            else:
                self.database().load(path)
            self.controller().update_title()
        except RuntimeError as e:
            self.main_widget().show_error(str(e))
            from mnemosyne.libmnemosyne.gui_translator import _
            self.main_widget().show_information(\
_("If you are using a USB key, refer to the instructions on the website so as not to be affected by drive letter changes."))
            # Try to open a new database, but not indefinitely, otherwise this
            # could turn a crash into a much nastier one on Android.
            success = False
            counter = 0
            while not success and counter <= 5:
                counter += 1
                try:
                    self.database().abandon()
                    self.controller().show_open_file_dialog()
                    success = True
                except RuntimeError as e:
                    self.main_widget().show_error(str(e))

    def start_review(self):
        self.controller().set_study_mode(self.study_mode_with_id(\
            self.config()["study_mode"]))
        # Design wart: log().load_database() needs the scheduler to be active,
        # so we can only call it here.
        self.log().loaded_database()
        # No need to log the future schedule everytime we change study
        # mode, so we only do it only on program start and roll-over.
        self.log().future_schedule()

    def finalise(self):
        # Deactivate the sync server first, so that we make sure it reverts
        # to the right backup file in case of problems.
        server = self.component_manager.current("sync_server")
        if server:
            server.deactivate()
        # Ditto for the web server.
        server = self.component_manager.current("web_server")
        if server:
            server.deactivate()
        # Saving the config should happen before we deactivate the plugins,
        # otherwise they are not restored upon reload.
        self.config().save()
        user_id = self.config()["user_id"]
        # We need to log before we unload the database.
        self.log().saved_database()
        self.log().stopped_program()
        # Now deactivate the database, such that deactivating plugins with
        # card types does not raise an error about card types in use.
        self.database().deactivate()
        self.component_manager.unregister(self.database())
        # Then do the review widget and other components.
        if self.review_widget():
            self.review_widget().deactivate()
        self.component_manager.deactivate_all()
        unregister_component_manager(user_id)
        if self.component_manager.debug_file:
            self.component_manager.debug_file.close()
