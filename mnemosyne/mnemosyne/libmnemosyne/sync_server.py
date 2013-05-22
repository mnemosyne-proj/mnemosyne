#
# sync_server.py <Peter.Bienstman@UGent.be>
#

import os
import mnemosyne.version

from openSM2sync.server import Server
from mnemosyne.libmnemosyne.utils import expand_path
from mnemosyne.libmnemosyne.component import Component


class SyncServer(Component, Server):

    """These are the libmnemosyne-specific parts of the openSH2sync server.
    Code to run the server in a separate thread is not provided here, as this
    is best done at the GUI level in view of the interaction between multiple
    threads and the GUI event loop.

    Also, a GUI will typically want to override/wrap 'load_database' and
    'unload_database', 'flush' too, because these will be subject to threading
    issues as well.

    """

    program_name = "Mnemosyne"
    program_version = mnemosyne.version.version

    def __init__(self, component_manager, ui):
        Component.__init__(self, component_manager)
        Server.__init__(self, self.config().machine_id(),
            self.config()["port_for_sync_as_server"], ui)
        self.check_for_edited_local_media_files = \
            self.config()["check_for_edited_local_media_files"]

    def authorise(self, username, password):
        return username == self.config()["remote_access_username"] and \
               password == self.config()["remote_access_password"]

    def load_database(self, database_name):
        self.previous_database = self.config()["last_database"]
        if self.previous_database != database_name:
            if not os.path.exists(expand_path(database_name,
                self.config().data_dir)):
                self.database().new(database_name)
            else:
                self.database().load(database_name)
        return self.database()

    def unload_database(self, database):
        self.database().load(self.previous_database)
        self.log().loaded_database()
        self.review_controller().reset_but_try_to_keep_current_card()
        self.review_controller().update_dialog(redraw_all=True)

    def flush(self):

        """If there are still dangling sessions (i.e. those waiting in vain
        for more client input) in the sync server, we should flush them and
        make sure they restore from backup before doing anything that could
        change the database (e.g. adding a card). Otherwise, if these
        sessions close later during program shutdown, their backup
        restoration will override the changes.

        """

        self.expire_old_sessions()


import threading
import socket

class SyncServerThread(threading.Thread, SyncServer):

    def __init__(self, component_manager):
        threading.Thread.__init__(self)
        SyncServer.__init__(self, component_manager, self)

    def run(self):
        try:
            self.serve_until_stopped()
        except socket.error:
            self.show_error(_("Unable to start sync server."))
        except Exception, e:
            self.show_error(str(e) + "\n" + traceback_string())
        # Clean up after stopping.
        server_hanging = (len(self.sessions) != 0)
        if server_hanging:
            self.terminate_all_sessions()
            self.database().release_connection()

    def show_information(self, message):
        print message

    def show_error(self, error):
        print error

    def show_question(self, question, option0, option1, option2):
        raise NotImplementedError # Server should ask questions anyway.

    def set_progress_text(self, text):
        pass

    def set_progress_range(self, maximum):
        pass

    def set_progress_update_interval(self, value):
        pass

    def increase_progress(self, value):
        pass

    def set_progress_value(self, value):
        pass

    def close_progress(self):
        pass

