    #
# mnemosyne_test.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import shutil
import time

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.ui_components.review_widget import ReviewWidget

class TestReviewWidget(ReviewWidget):

    def redraw_now(self):
        pass


class MnemosyneTest():
    @staticmethod
    def set_timezone_utc(fn):
        """
        Test decorator to set the timezone to UTC, and reset it on completion
        """
        if sys.platform == "win32":
            return fn

        def newfn(*args, **kwargs):
            oldtz = os.environ.get("TZ", None)
            os.environ["TZ"] = "UTC"
            time.tzset()
            try:
                fn(*args, **kwargs)
            finally:
                if oldtz is None:
                    os.environ.pop("TZ")
                else:
                    os.environ["TZ"] = oldtz
                time.tzset()
        return newfn

    def initialise_data_dir(self, data_dir="dot_test"):
        # Creating a new database seems a very time-consuming operation,
        # so we don't delete the test directory everytime, but take a short
        # cut.

        # Note: disabled this, as it does not seem to be very reliable.
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)
        assert not os.path.exists(data_dir)
        return

        if os.path.exists(data_dir):
            shutil.copy(os.path.join("mnemosyne", "tests", "files", "empty.db"),
                        os.path.join(data_dir, "default.db"))
            for directory in ["default.db_media", "plugins", "backups",
                              "history"]:
                full_path = str(os.path.join(data_dir, directory))
                if os.path.exists(full_path):
                    shutil.rmtree(full_path)
            for file in ["default.db-journal", "config",
                         "config.py", "machine.id", "log.txt"]:
                full_path = str(os.path.join(data_dir, file))
                if os.path.exists(full_path):
                    os.remove(full_path)

    def setup_method(self):
        self.initialise_data_dir()
        self.restart()

    def restart(self):
        # If there is another Mnemosyne still running, finalise it so as to
        # avoid having multiple component_managers active.
        if hasattr(self, "mnemosyne"):
            try:
                self.mnemosyne.finalise()
            except:
                pass
        path = os.path.join(os.getcwd(), "..", "mnemosyne", "libmnemosyne",
                            "renderers")
        if path not in sys.path:
            sys.path.append(path)
        self.mnemosyne = Mnemosyne(upload_science_logs=False,
            interested_in_old_reps=True, asynchronous_database=True)
        self.mnemosyne.components.insert(0,
            ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator",
             "GetTextGuiTranslator"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.gui_for_component["CramAll"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(os.path.abspath("dot_test"),
                                  automatic_upgrades=False)
        self.mnemosyne.start_review()

    def teardown_method(self):
        try:
            self.mnemosyne.finalise()
            # Avoid having multiple component_managers active.
            from mnemosyne.libmnemosyne.component_manager import clear_component_managers
            clear_component_managers()
        except: # Can throw some errors when we artificially mutilate plugins.
            self.mnemosyne.database().abandon()

    def config(self):
        return self.mnemosyne.component_manager.current("config")

    def log(self):
        return self.mnemosyne.component_manager.current("log")

    def database(self):
        return self.mnemosyne.component_manager.current("database")

    def scheduler(self):
        return self.mnemosyne.component_manager.current("scheduler")

    def main_widget(self):
        return self.mnemosyne.component_manager.current("main_widget")

    def review_widget(self):
        return self.mnemosyne.component_manager.current("review_widget")

    def controller(self):
        return self.mnemosyne.component_manager.current("controller")

    def review_controller(self):
        return self.mnemosyne.component_manager.current("review_controller")

    def card_types(self):
        return self.mnemosyne.component_manager.all("card_type")

    def filters(self):
        return self.mnemosyne.component_manager.all("filter")

    def plugins(self):
        return self.mnemosyne.component_manager.all("plugin")

    def render_chain(self, id="default"):
        return self.mnemosyne.component_manager.render_chain_with_id[id]

    def card_type_with_id(self, id):
        return self.mnemosyne.component_manager.card_type_with_id[id]


