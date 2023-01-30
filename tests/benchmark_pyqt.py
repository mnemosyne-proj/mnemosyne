#!/usr/bin/env python

import os
import time
import pstats
import cProfile

number_of_calls = 15 # Number of calls to display in profile
number_of_facts = 6000

def startup():

    import gettext
    _ = gettext.gettext

    import os
    import sys

    from optparse import OptionParser

    from PyQt6.QtGui import QApplication

    from mnemosyne.libmnemosyne import Mnemosyne

    # Parse options.

    parser = OptionParser()
    parser.usage = "%prog [<database_file>]"
    parser.add_option("-d", "--datadir", dest="data_dir",
                      help=_("data directory"), default=None)
    (options, args) = parser.parse_args()

    # Check if we have to override the data_dir determined in libmnemosyne,
    # either because we explicitly specified a data_dir on the command line,
    # or because there is a mnemosyne2 directory present in the current directory.
    # The latter is handy when Mnemosyne is run from a USB key, so that there
    # is no need to refer to a drive letter which can change from computer to
    # computer.
    data_dir = None
    if options.data_dir != None:
        data_dir = os.path.abspath(options.data_dir)
    elif os.path.exists(os.path.join(os.getcwd(), "mnemosyne2")):
        data_dir = os.path.abspath(os.path.join(os.getcwd(), "mnemosyne2"))

    # Filename argument.
    if len(args) > 0:
        filename = os.path.abspath(args[0])
    else:
        filename = None

    # Load the Mnemosyne library.
    mnemosyne = Mnemosyne(upload_science_logs=True)

    # Initialise GUI toolkit.
    a = QApplication(sys.argv)
    a.setApplicationName("Mnemosyne")
    # TODO: install translator for Qt messages.
    # Under Windows, move out of library.zip to get the true prefix.
    # from mnemosyne.pyqt_ui.main_window import prefix
    #if sys.platform == "win32":
    #    prefix = os.path.split(prefix)[0]
    #    prefix = os.path.split(prefix)[0]
    #    prefix = os.path.split(prefix)[0]
    #translator = QTranslator(a)
    #translator.load("qt_" + loc + ".qm", os.path.join(prefix, 'locale'))
    #a.installTranslator(translator)

    # Add other components we need. The GUI translator should obviously come first,
    # and the UI components should come in the order they should be instantiated,
    # but apart from that, the order does not matter.
    mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.gui_translator",
                                 "GetTextGuiTranslator"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.main_wdgt",
                                 "MainWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.review_wdgt",
                                 "ReviewWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.configuration",
                                 "PyQtConfiguration"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.pyqt_render_chain",
                                 "PyQtRenderChain"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.add_cards_dlg",
                                 "AddCardsDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.edit_card_dlg",
                                 "EditCardDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.browse_cards_dlg",
                                 "BrowseCardsDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.activate_cards_dlg",
                                 "ActivateCardsDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.cloned_card_types_list_dlg",
                                 "ClonedCardTypesListDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.card_appearance_dlg",
                                 "CardAppearanceDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.activate_plugins_dlg",
                                 "ActivatePluginsDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.statistics_dlg",
                                 "StatisticsDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.card_type_wdgt_generic",
                                 "GenericCardTypeWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.statistics_wdgts_plotting",
                                 "ScheduleWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.statistics_wdgts_plotting",
                                 "RetentionScoreWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.statistics_wdgts_plotting",
                                 "GradesWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.statistics_wdgts_plotting",
                                 "EasinessWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.statistics_wdgts_plotting",
                                 "CardsAddedWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.statistics_wdgt_html",
                                 "HtmlStatisticsWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.criterion_wdgt_default",
                                 "DefaultCriterionWdgt"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.configuration_dlg",
                                 "ConfigurationDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.sync_dlg",
                                 "SyncDlg"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.qt_sync_server",
                                 "QtSyncServer"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.configuration_wdgt_main",
                                 "ConfigurationWdgtMain"))
    mnemosyne.components.append(("mnemosyne.pyqt_ui.configuration_wdgt_sync_server",
                                 "ConfigurationWdgtSyncServer"))

    # Run Mnemosyne.
    mnemosyne.initialise(data_dir=data_dir, filename=filename)
    mnemosyne.main_widget().show()
    mnemosyne.main_widget().raise_() # Needed for OSX.
    # TODO: check first run wizard.
    #if config()["first_run"] == True:
    #    w.productTour()
    #    config()["first_run"] = False
    #elif config()["show_daily_tips"] == True:
    #    w.Tip()

    a.exec()
    mnemosyne.finalise()


tests = ["startup()"]

for test in tests:
    cProfile.run(test, "mnemosyne_profile." + test.replace("()", ""))
    print()
    print(("*** ", test, " ***"))
    print()
    p = pstats.Stats('mnemosyne_profile.' + test.replace("()", ""))
    p.strip_dirs().sort_stats('cumulative').print_stats(number_of_calls)


