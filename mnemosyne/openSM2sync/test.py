import sys
import os
sys.path.insert(0, '../../')
sys.path.insert(0, "../")
from libSM2sync.server import Server
from libSM2sync.client import Client
from maemo_ui.factory import app_factory

def main(argv):
    """Main."""

    if len(argv) < 3:
        print "USAGE: %s MODE HOST:PORT" % argv[0]
    else:
        mode = argv[1]
        uri = argv[2]
        if mode == "server":
            app = app_factory()
            #app.initialise(os.path.abspath(os.path.join(os.getcwdu(), ".mnemosyne")))
            app.initialise(os.path.abspath(os.path.join(os.getcwdu(), "testdb")))
            database = app.database()
            server = Server(uri, database, app.config(), app.log())
            server.start()
            app.finalise()
        elif mode == "client":
            app = app_factory()
            #app.initialise(os.path.abspath(os.path.join(os.getcwdu(), "testdb")))
            app.initialise(os.path.abspath(os.path.join(os.getcwdu(), ".mnemosyne")))
            database = app.database()
            client = Client(uri, database, app.controller(), app.config(), app.log())
            client.start()
            app.finalise()
        else:
            print "unknown mode"


if __name__ == "__main__":
    sys.exit(main(sys.argv))


def TODO:
    
    def start_client_sync_cb(self, widget):
        """Starts syncing as Client."""

        if not widget.get_active():
            self.show_or_hide_containers(False, "client")
            login = self.get_widget("sync_mode_client_login_entry").get_text()
            passwd = self.get_widget("sync_mode_client_passwd_entry").get_text()
            host = self.get_widget(\
                "sync_mode_client_address_entry").get_text()
            port = self.get_widget("sync_mode_client_port_entry").get_text()
            uri = host + ':' + port
            if not uri.startswith("http://"):
                uri = "http://" + uri
            messenger = UIMessenger(self.show_message, self.complete_events, \
                self.update_client_status, self.client_progressbar.show, \
                self.update_client_progressbar, self.client_progressbar.hide)
            self.client = Client(host, port, uri, self.database(), \
                self.controller(), self.config(), self.log(), messenger)
            self.client.set_user(login, passwd)
            self.complete_events()
            self.client.start()
            self.show_or_hide_containers(True, "client")
            self.get_widget(\
                "sync_mode_client_start_button").set_active(False)
        else:
            self.show_or_hide_containers(True, "client")
            self.client.stop()
            self.client = None

    def start_server_sync_cb(self, widget):
        """Starts syncing as Server."""

        if not widget.get_active():
            try:
                port = int(self.get_widget(\
                    "sync_mode_server_port_entry").get_text())
            except ValueError:
                self.main_widget().error_box("Wrong port number!")
            else:
                host = self.get_widget(\
                    "sync_mode_server_address_entry").get_text()
                self.show_or_hide_containers(False, "server")
                try:
                    messenger = UIMessenger(self.show_message, \
                    self.complete_events, self.update_server_status, \
                    self.server_progressbar.show, \
                    self.update_server_progressbar, \
                    self.server_progressbar.hide)
                    self.server = Server("%s:%s" % (host, port), \
                    self.database(), self.config(), self.log(), messenger)
                except socket.error, error:
                    self.show_message(str(error))
                else:
                    self.server.set_user(\
                        self.get_widget("sync_mode_server_login_entry"). \
                            get_text(), 
                        self.get_widget("sync_mode_server_passwd_entry"). \
                            get_text())
                    self.server.start()
                self.show_or_hide_containers(True, "server")
                self.get_widget(\
                    "sync_mode_server_start_button").set_active(False)
        else:
            self.show_or_hide_containers(True, "server")
            self.server.stop()
            self.server = None
