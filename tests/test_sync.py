#
# test_sync.py <Peter.Bienstman@UGent.be>
#

import os
import sys
import time
import shutil
import http.client
from pytest import raises
from threading import Thread, Condition

from openSM2sync.server import Server
from openSM2sync.client import Client
from openSM2sync.log_entry import EventTypes

from mnemosyne.version import version
from mnemosyne_test import MnemosyneTest

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget
from mnemosyne.libmnemosyne.criteria.default_criterion import DefaultCriterion

server_initialised = Condition()
server_is_initialised = None
tests_done = Condition()

last_error = None
answer = None

class Widget(MainWidget):

    def set_progress_text(self, message):
        print(message)
        #sys.stderr.write(message+'\n')

    def show_information(self, info):
        print(info)
        #sys.stderr.write(info+'\n')

    def show_error(self, error):
        global last_error
        last_error = error
        # Activate this for debugging.
        print(error)
        #sys.stderr.write(error)

    def show_question(self, question, option0, option1, option2):
        #sys.stderr.write(question+'\n')
        return answer

    def get_filename_to_save(self, path, filter, caption):
        return "default.db"


PORT = 9923

class MyServer(Server, Thread):

    program_name = "Mnemosyne"
    program_version = version
    user_id = "user_id"

    def __init__(self, data_dir=os.path.abspath("dot_sync_server"),
            filename="default.db", binary_download=False, erase_previous=True):
        self.binary_download = binary_download
        self.data_dir = data_dir
        self.filename = filename
        Thread.__init__(self)
        if erase_previous:
            MnemosyneTest().initialise_data_dir(data_dir)
            assert not os.path.exists(data_dir)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(("test_sync", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        global server_is_initialised
        server_is_initialised = None
        self.passed_tests = None

    def authorise(self, login, password):
        return login == "user" and password == "pass"

    def load_database(self, database_name):
        self.mnemosyne.database().load(database_name)
        return self.mnemosyne.database()

    def unload_database(self, database_name):
        self.mnemosyne.database().release_connection()

    def run(self):
        # We only open the database connection inside the thread to prevent
        # access problems, as a single connection can only be used inside a
        # single thread.
        # We use a condition object here to prevent the client from accessing
        # the server until the server is ready.
        server_initialised.acquire()
        self.mnemosyne.initialise(self.data_dir, config_dir=self.data_dir,
            filename=self.filename, automatic_upgrades=False)
        self.mnemosyne.config().change_user_id(self.user_id)
        self.mnemosyne.review_controller().reset()
        if hasattr(self, "fill_server_database"):
            self.fill_server_database(self)
        self.unload_database(self.filename)
        Server.__init__(self, self.mnemosyne.config().machine_id(),
                        PORT, self.mnemosyne.main_widget())
        self.check_for_edited_local_media_files = True
        if not self.binary_download:
            self.supports_binary_transfer = lambda x : False
        global server_is_initialised
        server_is_initialised = True
        server_initialised.notify()
        server_initialised.release()
        try:
            self.serve_until_stopped()
        except Exception as e: # Socket not ready.
            time.sleep(0.3)
            self.serve_until_stopped()
        # Also running the actual tests we need to do inside this thread and
        # not in the main thread, again because of sqlite access restrictions.
        # However, if the asserts fail in this thread, nose won't flag them as
        # failures in the main thread, so we communicate failure back to the
        # main thread using self.passed_tests.
        tests_done.acquire()
        self.passed_tests = False
        try:
            self.test_server(self)
            self.passed_tests = True
        finally:
            self.mnemosyne.database().release_connection()
            self.mnemosyne.finalise()
            tests_done.notify()
            tests_done.release()

    def stop(self):
        import socket; socket.setdefaulttimeout(.010)
        Server.stop(self)
        # Make an extra request so that we don't need to wait for the server
        # timeout. This could fail if the server has already shut down.
        try:
            con = http.client.HTTPConnection("localhost", PORT)
            con.request("GET", "dummy_request")
            con.getresponse().read()
        except:
            pass
        global server_is_initialised
        server_is_initialised = None


class MyClient(Client):

    program_name = "Mnemosyne"
    program_version = version
    capabilities = "mnemosyne_dynamic_cards"
    user = "user"
    password = "pass"
    exchange_settings = False
    binary_upload = False

    def __init__(self, data_dir=os.path.abspath("dot_sync_client"),
            filename="default.db", erase_previous=True):
        if erase_previous:
            MnemosyneTest().initialise_data_dir(data_dir)
            #shutil.rmtree(unicode(data_dir), ignore_errors=True)
        self.mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=False,
            asynchronous_database=True)
        self.mnemosyne.components.insert(0,
           ("mnemosyne.libmnemosyne.gui_translators.gettext_gui_translator", "GetTextGuiTranslator"))
        self.mnemosyne.components.append(("test_sync", "Widget"))
        self.mnemosyne.gui_for_component["ScheduledForgottenNew"] = \
            [("mnemosyne_test", "TestReviewWidget")]
        self.mnemosyne.initialise(data_dir, config_dir=data_dir, filename=filename,  automatic_upgrades=False)
        self.mnemosyne.config().change_user_id("user_id")
        self.mnemosyne.review_controller().reset()
        Client.__init__(self, self.mnemosyne.config().machine_id(),
                        self.mnemosyne.database(), self.mnemosyne.main_widget())

    def supports_binary_upload(self):
        # Make sure we excercise the text protocol.
        return self.binary_upload

    def do_sync(self):
        server_initialised.acquire()
        while not server_is_initialised:
            server_initialised.wait()
        server_initialised.release()
        # The mechanism above turned out to be not enough, as Cherrypy also
        # has an internal delay to start up the server.
        global last_error
        for i in range(20):
            last_error = None
            self.sync("localhost", PORT, self.user, self.password)
            if not last_error or not "Could not connect to server" in last_error:
                return
            time.sleep(0.3)



class TestSync(object):

    def _wait_for_server_shutdown(self):
        tests_done.acquire()
        while self.server.passed_tests is None:
            tests_done.wait()
        tests_done.release()

    def teardown_method(self):
        if self.server is None:
            self.client.mnemosyne.finalise()
            return
        self.server.stop()
        self._wait_for_server_shutdown()
        try:
            assert self.server.passed_tests == True
        finally:
            self.client.mnemosyne.finalise()

    def test_copied_database(self):

        global last_error

        def test_server(self):
            pass

        def fill_server_database(self):
            fact_data = {"f": "question",
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()

        self.server.stop()
        self._wait_for_server_shutdown()

        if os.path.exists(os.path.abspath("dot_sync_client")):
            shutil.rmtree(str(os.path.abspath("dot_sync_client")))
        shutil.copytree(os.path.abspath("dot_sync_server"),
            os.path.abspath("dot_sync_client"))

        self.server = MyServer(erase_previous=False)
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient(erase_previous=False)

        self.client.do_sync();
        assert "copied" in last_error
        last_error = None

    def test_sync_empty_twice(self):

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        # Do full binary sync

        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()

        # Second sync.
        self.client = MyClient(erase_previous=False)
        self.client.do_sync(); assert last_error is None

    def test_sync_issue(self):

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        # Do full binary sync

        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            fact_data = {"f": "question",
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

        self.server = MyServer(erase_previous=False)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.do_sync(); assert last_error is None

    def test_machine_id(self):

        def test_server(self):
            assert self.mnemosyne.database().con.execute(\
                "select count(distinct object_id) from log where event_type=?",
               (EventTypes.LOADED_DATABASE, )).fetchone()[0] == 4

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.server.client_machine_id = \
            self.client.mnemosyne.config().machine_id()
        # Do full binary sync
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()

        # Second sync.
        self.client = MyClient(erase_previous=False)
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name(chr(0x628) + ">&<abcd")
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count(distinct object_id) from log where event_type=?",
               (EventTypes.LOADED_DATABASE, )).fetchone()[0] == 4

    def test_add_tag(self):

        def test_server(self):
            db = self.mnemosyne.database()
            tag = db.get_or_create_tag_with_name(chr(0x628) + '>&<abcd')
            assert tag.id == self.client_tag_id
            assert tag.name == chr(0x628) + ">&<abcd"
            sql_res = db.con.execute("select timestamp from log where event_type=?",
               (EventTypes.ADDED_TAG, )).fetchone()
            assert self.tag_added_timestamp == sql_res[0]
            assert type(sql_res[0]) == int
            assert db.con.execute("select count() from log").fetchone()[0] == 23

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name(chr(0x628) + ">&<abcd")
        self.server.client_tag_id = tag.id
        sql_res = self.client.mnemosyne.database().con.execute(\
            "select timestamp from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()
        self.server.tag_added_timestamp = sql_res[0]
        assert type(self.server.tag_added_timestamp) == int
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()[0] == 1
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 23

    # The next two tests are a bit problematic in the sense that both client
    # and server share the same component_manager here, so we can't really
    # check proper behaviour.

    def test_change_server_user_id(self):

        def test_server(self):
            assert self.mnemosyne.config()["user_id"] == "funky"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.mnemosyne.database().get_or_create_tag_with_name("test")
        self.client.mnemosyne.config().change_user_id("funky")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_change_server_user_id_binary_upload(self):

        def test_server(self):
            assert self.mnemosyne.config()["user_id"] == "funky"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.mnemosyne.database().get_or_create_tag_with_name("test")
        self.client.binary_upload = True
        self.client.mnemosyne.config().change_user_id("funky")

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_tag_behind_proxy(self):

        def test_server(self):
            db = self.mnemosyne.database()
            tag = db.get_or_create_tag_with_name(chr(0x628) + '>&<abcd')
            assert tag.id == self.client_tag_id
            assert tag.name == chr(0x628) + ">&<abcd"
            sql_res = db.con.execute("select timestamp from log where event_type=?",
               (EventTypes.ADDED_TAG, )).fetchone()
            assert self.tag_added_timestamp == sql_res[0]
            assert type(sql_res[0]) == int
            assert db.con.execute("select count() from log").fetchone()[0] == 23

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.behind_proxy = True
        self.client.BUFFER_SIZE = 1
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name(chr(0x628) + ">&<abcd")
        self.server.client_tag_id = tag.id
        sql_res = self.client.mnemosyne.database().con.execute(\
            "select timestamp from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()
        self.server.tag_added_timestamp = sql_res[0]
        assert type(self.server.tag_added_timestamp) == int
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()[0] == 1
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 23
        assert self.server.is_sync_in_progress() == False

    def test_add_tag_controller(self):

        def test_server(self):
            db = self.mnemosyne.database()
            tag = db.get_or_create_tag_with_name(chr(0x628) + '>&<abcd')
            assert tag.id == self.client_tag_id
            assert tag.name == chr(0x628) + ">&<abcd"
            sql_res = db.con.execute("select timestamp from log where event_type=?",
               (EventTypes.ADDED_TAG, )).fetchone()
            assert self.tag_added_timestamp == sql_res[0]
            assert type(sql_res[0]) == int
            assert db.con.execute("select count() from log").fetchone()[0] == 23

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name(chr(0x628) + ">&<abcd")
        self.server.client_tag_id = tag.id
        sql_res = self.client.mnemosyne.database().con.execute(\
            "select timestamp from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()
        self.server.tag_added_timestamp = sql_res[0]
        assert type(self.server.tag_added_timestamp) == int
        self.client.mnemosyne.controller().save_file()
        self.client.mnemosyne.controller().sync("localhost", PORT,
             self.client.user, self.client.password); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()[0] == 1
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 23

    def test_edit_tag(self):

        def test_server(self):
            db = self.mnemosyne.database()
            tag = db.tag(self.client_tag_id, is_id_internal=False)
            assert tag.extra_data["b"] == "<a>"
            assert db.con.execute("select count() from log").\
                   fetchone()[0] == 24

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name("tag")
        tag.extra_data = {"b": "<a>"}
        self.client.mnemosyne.database().update_tag(tag)
        self.server.client_tag_id = tag.id
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 24

    def test_delete_tag(self):
        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from tags where id=?",
                (self.client_tag_id, )).fetchone()[0] == 0
            assert db.con.execute("select count() from log").\
                   fetchone()[0] == 26

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.mnemosyne.database().delete_tag(tag)
        self.server.client_tag_id = tag.id
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
                "select count() from log").fetchone()[0] == 26

    def test_add_fact(self):

        def test_server(self):
            db = self.mnemosyne.database()
            fact = db.fact(self.client_fact_id, is_id_internal=False)
            assert fact.data == {"f": "f"}
            assert db.con.execute("select count() from log").fetchone()[0] == 22

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        card_type = self.client.mnemosyne.card_type_with_id("1")
        fact = Fact({"f": "f"})
        self.client.mnemosyne.database().add_fact(fact)
        self.server.client_fact_id = fact.id
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 22

    def test_edit_fact(self):

        def test_server(self):
            db = self.mnemosyne.database()
            fact = db.fact(self.client_fact_id, is_id_internal=False)
            assert fact.data == {"f": "f", "b": "AA"}
            assert db.con.execute("select count() from log").fetchone()[0] == 23

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        card_type = self.client.mnemosyne.card_type_with_id("1")
        fact = Fact({"f": "f", "b": "b"})
        self.client.mnemosyne.database().add_fact(fact)
        fact.data = {"f": "f", "b": "AA"}
        self.client.mnemosyne.database().update_fact(fact)
        self.server.client_fact_id = fact.id
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 23

    def test_delete_fact(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from facts where id=?",
                (self.client_fact_id, )).fetchone()[0] == 0
            assert db.con.execute("select count() from log").fetchone()[0] == 25

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        card_type = self.client.mnemosyne.card_type_with_id("1")
        fact = Fact({"f": "f", "b": "b"})
        self.client.mnemosyne.database().add_fact(fact)
        self.client.mnemosyne.controller().save_file()
        self.client.mnemosyne.database().delete_fact(fact)
        self.server.client_fact_id = fact.id
        self.client.mnemosyne.controller().save_file()
        self.client.mnemosyne.log().stopped_program()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 25

    def test_add_cards(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.fact_count() == 1
            assert db.card_count() == 1
            card = db.card(self.client_card.id, is_id_internal=False)
            assert card.question() == self.client_card.question()
            tag_ids = [tag.id for tag in card.tags]
            assert db.get_or_create_tag_with_name("tag_1").id in tag_ids
            assert db.get_or_create_tag_with_name("tag_2").id in tag_ids
            assert len(card.tags) == 2
            assert card.card_type == self.mnemosyne.card_type_with_id("1")
            assert card.creation_time == self.client_card.creation_time
            assert card.modification_time == self.client_card.modification_time
            assert card.scheduler_data == 0
            assert card.active == True
            assert card.grade == 4
            assert card.easiness == 2.5
            assert card.acq_reps == 1
            assert card.ret_reps == 0
            assert card.lapses == 0
            assert card.acq_reps_since_lapse == 1
            assert card.ret_reps_since_lapse == 0
            assert card.last_rep != -1
            assert card.next_rep != -1
            assert db.con.execute("select count() from log").fetchone()[0] == 28
            assert card.id == self.client_card.id

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.server.client_card = card
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 28

    def test_edit_cards(self):

        def test_server(self):
            db = self.mnemosyne.database()
            card = db.card(self.client_card.id, is_id_internal=False)
            assert card.extra_data == {"A": "B"}
            assert db.con.execute("select count() from log").fetchone()[0] == 29
            assert card.card_type == self.mnemosyne.card_type_with_id("1")
            assert card.creation_time == self.client_card.creation_time
            assert card.modification_time == self.client_card.modification_time

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.server.client_card = card
        card.extra_data = {"A": "B"}
        self.client.database.update_card(card)
        self.server.client_card = card
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 29

    def test_delete_tag_2(self):

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        def test_server(self):
            db = self.mnemosyne.database()
            card = db.card(self.client_card.id, is_id_internal=False)
            tag_string = db.con.execute("select tags from cards where _id=?",
                (card._id,)).fetchone()[0]
            assert "tag_1" not in tag_string
            assert db.con.execute("select count() from log").fetchone()[0] == 52

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.mnemosyne.review_controller().reset()
        self.server.client_card = card

        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag_1")
        self.client.mnemosyne.database().delete_tag(tag)
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 52

    def test_rename_tag(self):

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        def test_server(self):
            db = self.mnemosyne.database()
            card = db.card(self.client_card.id, is_id_internal=False)
            tag_string = db.con.execute("select tags from cards where _id=?",
                (card._id,)).fetchone()[0]
            assert "TAG_1" in tag_string
            assert "tag_1" not in tag_string
            assert db.con.execute("select count() from log").fetchone()[0] == 51

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.mnemosyne.review_controller().reset()
        self.server.client_card = card

        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag_1")
        tag.name = "TAG_1"
        self.client.mnemosyne.database().update_tag(tag)
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 51

    def test_delete_cards(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from cards where id=?",
                (self.client_card.id, )).fetchone()[0] == 0
            assert db.con.execute("select count() from facts").fetchone()[0] == 0
            assert db.con.execute("select count() from tags").fetchone()[0] == 1
            assert db.con.execute("select count() from log").fetchone()[0] == 34

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.server.client_card = card
        self.client.mnemosyne.controller().delete_facts_and_their_cards([card.fact])
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 34

    def test_repetition(self):

        def test_server(self):
            db = self.mnemosyne.database()
            card = db.card(self.client_card.id, is_id_internal=False)
            assert card.grade == self.client_card.grade
            assert card.easiness == self.client_card.easiness
            assert card.acq_reps == self.client_card.acq_reps
            assert card.ret_reps == self.client_card.ret_reps
            assert card.lapses == self.client_card.lapses
            assert card.acq_reps_since_lapse == self.client_card.acq_reps_since_lapse
            assert card.ret_reps_since_lapse == self.client_card.ret_reps_since_lapse
            assert card.last_rep == self.client_card.last_rep
            assert card.next_rep == self.client_card.next_rep
            assert card.scheduler_data == self.client_card.scheduler_data

            rep =  db.con.execute("""select * from log where event_type=? order by
                _id desc limit 1""", (EventTypes.REPETITION, )).fetchone()
            assert rep[4] == 5
            assert rep[5] == 2.5
            assert rep[6] == 1
            assert rep[7] == 1
            assert rep[8] == 0
            assert rep[9] == 1
            assert rep[10] == 1
            assert rep[11] > 60*60
            assert rep[12] < 10
            assert rep[14] - rep[2] > 60*60
            assert rep[13] < 10
            assert rep[2] > 0

            assert db.con.execute("select count() from log").fetchone()[0] == 29

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.review_controller().learning_ahead = True
        self.client.mnemosyne.review_controller().show_new_question()
        self.client.mnemosyne.review_controller().grade_answer(5)
        self.client.mnemosyne.controller().save_file()
        self.server.client_card = self.client.mnemosyne.database().\
           card(card.id, is_id_internal=False)
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 29

    def test_add_media(self):

        def fill_server_database(self):
            os.mkdir(os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b"))

            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b", chr(0x628) + "b..ogg")
            f = open(filename, "w")
            f.write("B")
            f.close()
            fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().save_file()

        def test_server(self):
            db = self.mnemosyne.database()
            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "a", chr(0x628) + "a..ogg")
            assert os.path.exists(filename)
            assert open(filename).read() == "A"
            assert db.con.execute("select count() from log").fetchone()[0] == 38
            assert db.con.execute("select count() from log where event_type=?",
                (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 2
            assert db.con.execute("""select object_id from log where event_type=?
                order by _id desc limit 1""", (EventTypes.ADDED_MEDIA_FILE, )).\
                fetchone()[0].startswith("a/")
            assert db.con.execute("select count() from media").fetchone()[0] == 2
            card = db.card(self.client_card.id, is_id_internal=False)
            assert card.fact["f"].startswith("question\n<img src=")

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()

        os.mkdir(os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a"))

        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a", chr(0x628) + "a..ogg")
        f = open(filename, "w")
        f.write("A")
        f.close()
        fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().save_file()
        self.server.client_card = self.client.mnemosyne.database().\
            card(card.id, is_id_internal=False)
        self.client.do_sync(); assert last_error is None

        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "b", chr(0x628) + "b..ogg")
        assert os.path.exists(filename)
        assert open(filename).read() == "B"
        db = self.client.mnemosyne.database()
        assert db.con.execute("select count() from log").fetchone()[0] == 38
        assert db.con.execute("select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 2
        assert db.con.execute("select count() from media").fetchone()[0] == 2
        assert db.con.execute("""select object_id from log where event_type=?
            order by _id desc limit 1""", (EventTypes.ADDED_MEDIA_FILE, )).\
            fetchone()[0].startswith("b/")


    def test_add_delete_add_media(self):

            def fill_server_database(self):
                os.mkdir(os.path.join(os.path.abspath("dot_sync_server"),
                    "default.db_media", "b"))

                filename = os.path.join(os.path.abspath("dot_sync_server"),
                    "default.db_media", "b", chr(0x628) + "b..ogg")
                f = open(filename, "w")
                f.write("B")
                f.close()

                fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                             "b": "answer"}
                card_type = self.mnemosyne.card_type_with_id("1")
                card = self.mnemosyne.controller().create_new_cards(fact_data,
                   card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

                new_fact_data = {"f": "question", "b": "answer"}
                self.mnemosyne.controller().edit_card_and_sisters(card, new_fact_data,
                    card_type, ["tag_1", "tag_2"], {})
                self.mnemosyne.database().delete_unused_media_files(\
                    self.mnemosyne.database().unused_media_files())

                os.mkdir(os.path.join(os.path.abspath("dot_sync_server"),
                    "default.db_media", "b"))
                f = open(filename, "w")
                f.write("B")
                f.close()

                self.mnemosyne.controller().edit_card_and_sisters(card, fact_data,
                    card_type, ["tag_1", "tag_2"], {})

                self.mnemosyne.controller().save_file()

            def test_server(self):
                pass

            self.server = MyServer()
            self.server.test_server = test_server
            self.server.fill_server_database = fill_server_database
            self.server.start()

            self.client = MyClient()

            self.client.do_sync(); assert last_error is None

            filename = os.path.join(os.path.abspath("dot_sync_client"),
                "default.db_media", "b", chr(0x628) + "b..ogg")
            assert os.path.exists(filename)
            assert open(filename).read() == "B"

    def test_add_media_behind_proxy(self):

        def fill_server_database(self):
            os.mkdir(os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b"))

            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b", chr(0x628) + "b.ogg")
            f = open(filename, "w")
            f.write("B")
            f.close()
            fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().save_file()

        def test_server(self):
            db = self.mnemosyne.database()
            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "a", chr(0x628) + "a.ogg")
            assert os.path.exists(filename)
            assert open(filename).read() == "A"
            assert db.con.execute("select count() from log").fetchone()[0] == 38
            assert db.con.execute("select count() from log where event_type=?",
                (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 2
            assert db.con.execute("""select object_id from log where event_type=?
                order by _id desc limit 1""", (EventTypes.ADDED_MEDIA_FILE, )).\
                fetchone()[0].startswith("a/")
            assert db.con.execute("select count() from media").fetchone()[0] == 2
            card = db.card(self.client_card.id, is_id_internal=False)
            assert card.fact["f"].startswith("question\n<img src=")

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.behind_proxy = True

        os.mkdir(os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a"))

        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a", chr(0x628) + "a.ogg")
        f = open(filename, "w")
        f.write("A")
        f.close()
        fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().save_file()
        self.server.client_card = self.client.mnemosyne.database().\
            card(card.id, is_id_internal=False)
        self.client.do_sync(); assert last_error is None
        assert self.server.is_idle() == True

        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "b", chr(0x628) + "b.ogg")
        assert os.path.exists(filename)
        assert open(filename).read() == "B"
        db = self.client.mnemosyne.database()
        assert db.con.execute("select count() from log").fetchone()[0] == 38
        assert db.con.execute("select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 2
        assert db.con.execute("select count() from media").fetchone()[0] == 2
        assert db.con.execute("""select object_id from log where event_type=?
            order by _id desc limit 1""", (EventTypes.ADDED_MEDIA_FILE, )).\
            fetchone()[0].startswith("b/")

    def test_delete_card_with_media(self):

        def fill_server_database(self):
            os.mkdir(os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b"))

            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b", chr(0x628) + "b.ogg")
            f = open(filename, "w")
            f.write("B")
            f.close()
            fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().delete_facts_and_their_cards([card.fact])
            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()

        os.mkdir(os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a"))

        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a", chr(0x628) + "a.ogg")
        f = open(filename, "w")
        f.write("A")
        f.close()
        fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().delete_facts_and_their_cards([card.fact])
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_check_for_edited_media_files(self):

        def fill_server_database(self):
            os.mkdir(os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b"))

            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b", chr(0x628) + "b.ogg")
            f = open(filename, "w")
            f.write("B")
            f.close()
            fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().delete_facts_and_their_cards([card.fact])
            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.check_for_edited_local_media_files = True
        self.server.start()

        self.client = MyClient()

        os.mkdir(os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a"))

        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a", chr(0x628) + "a.ogg")
        f = open(filename, "w")
        f.write("A")
        f.close()
        fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                     "b": "answer"}
        self.client.check_for_edited_local_media_files = True
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().delete_facts_and_their_cards([card.fact])
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_star_twice(self):

        def fill_server_database(self):
            pass

        def test_server(self):
            card = self.mnemosyne.database().card(self.client_card.id, is_id_internal=False)
            assert len(card.tags) == 1
            assert list(card.tags)[0].name == "Starred"

        self.server = MyServer(binary_download=False)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.check_for_edited_local_media_files = False
        self.server.start()

        self.client = MyClient()
        self.client.check_for_edited_local_media_files = False

        card_type = self.client.mnemosyne.card_type_with_id("2")
        fact_data = {"f": "question",
                     "b": "answer"}
        card_1 = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=-1, tag_names=[])[0]

        fact_data = {"f": "question2",
                     "b": "answer"}
        card_2 = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=-1, tag_names=[])[0]

        assert self.client.mnemosyne.database().fact_count() == 2
        assert self.client.mnemosyne.database().card_count() == 4

        self.client.mnemosyne.review_controller().reset()
        self.server.client_card = self.client.mnemosyne.review_controller().card
        self.client.mnemosyne.controller().star_current_card()
        self.client.mnemosyne.controller().star_current_card()
        self.client.mnemosyne.review_controller().grade_answer(5)
        self.client.mnemosyne.controller().star_current_card()
        self.client.mnemosyne.controller().star_current_card()
        self.client.mnemosyne.review_controller().grade_answer(5)
        self.client.mnemosyne.controller().star_current_card()
        self.client.mnemosyne.controller().star_current_card()
        self.client.mnemosyne.review_controller().grade_answer(5)
        self.client.mnemosyne.controller().star_current_card()
        self.client.mnemosyne.controller().star_current_card()
        self.client.mnemosyne.review_controller().grade_answer(5)

        self.client.do_sync(); assert last_error is None

    def test_delete_media(self):

        # We cannot delete media during sync.


        # First sync.

        def test_server(self):
            filename = os.path.join(os.path.abspath("dot_sync_server"),
            "default.db_media", "a", chr(0x628) + "a.ogg")
            #assert os.path.exists(filename)

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        os.mkdir(os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a"))
        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a", chr(0x628) + "a.ogg")
        f = open(filename, "w")
        f.write("A")
        f.close()
        fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]

        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            pass

        def test_server(self):
            #assert self.mnemosyne.database().con.execute("select count() from log where event_type=?",
            #    (EventTypes.DELETED_MEDIA_FILE, )).fetchone()[0] == 1
            filename = os.path.join(os.path.abspath("dot_sync_server"),
            "default.db_media", "a", chr(0x628) + "a.ogg")
            #assert not os.path.exists(filename)

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()
        self.server.card_id = card.id

        self.client = MyClient(erase_previous=False)

        self.client.mnemosyne.controller().delete_facts_and_their_cards([card.fact])
        unused_files = self.client.mnemosyne.database().unused_media_files()
        self.client.mnemosyne.database().delete_unused_media_files(unused_files)
        self.client.mnemosyne.controller().save_file()

        self.client.do_sync(); assert last_error is None
        #assert not os.path.exists(filename)

    def test_edit_tag_2(self):
        # First sync.

        def test_server(self):
            pass

        def fill_server_database(self):
            card_type = self.mnemosyne.card_type_with_id("1")
            fact_data = {"f": "question",
                         "b": "answer"}
            self.card = self.mnemosyne.controller().create_new_cards(\
                fact_data, card_type, grade=-1, tag_names=["xx::new::vb::test"])[0]
            fact_data = {"f": "question2",
                         "b": "answer2"}
            self.mnemosyne.controller().create_new_cards(\
                fact_data, card_type, grade=-1, tag_names=["xx::vb::test"])

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()

        self.client.do_sync(); assert last_error is None
        card = self.server.card
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            from mnemosyne.libmnemosyne.tag_tree import TagTree
            self.tree = TagTree(self.mnemosyne.component_manager)
            self.tree.rename_node("xx::new::vb::test", "xx::vb::test")

        def test_server(self):
            pass

        self.server = MyServer(erase_previous=False, binary_download=False)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.do_sync(); assert last_error is None

        card = self.client.database.card(card._id, is_id_internal=True)
        assert len(card.tags) == 1
        assert list(card.tags)[0].name == "xx::vb::test"
        assert self.client.database.con.execute(\
            "select tags from cards where _id=?", (card._id,)).fetchone()[0] == "xx::vb::test"
        assert self.client.database.con.execute(\
            "select count() from tags_for_card").fetchone()[0] == 2

    def test_edit_media(self):

        def test_server(self):
            db = self.mnemosyne.database()
            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "a.ogg")
            assert os.path.exists(filename)
            assert open(filename).read() == "B"
            assert db.con.execute("""select count() from media""").fetchone()[0] == 1
            assert db.con.execute("select count() from log").fetchone()[0] == 30
            assert db.con.execute("select count() from log where event_type=?",
                (EventTypes.EDITED_MEDIA_FILE, )).fetchone()[0] == 1

            sql_res = db.con.execute("select _hash, filename from media").fetchone()
            assert sql_res[0] == db._media_hash(sql_res[1])

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a.ogg")
        f = open(filename, "w")
        f.write("A")
        f.close()

        fact_data = {"f": "question <img src=\"%s\">" % (filename),
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().save_file()

        db = self.client.mnemosyne.database()
        sql_res = db.con.execute("select _hash, filename from media").fetchone()
        assert sql_res[0] == db._media_hash(sql_res[1])

        # Sleep 1 sec to make sure the timestamp detection mechanism works.
        import time; time.sleep(1)

        f = open(filename, "w")
        f.write("B")
        f.close()

        self.client.do_sync(); assert last_error is None

        sql_res = db.con.execute("select _hash, filename from media").fetchone()
        assert sql_res[0] == db._media_hash(sql_res[1])

        assert db.con.execute("select count() from log where event_type=?",
            (EventTypes.EDITED_MEDIA_FILE, )).fetchone()[0] == 1
        assert db.con.execute("select count() from log").fetchone()[0] == 30

    def test_anki_import(self):

        def fill_server_database(self):
            filename = os.path.join(os.getcwd(), "tests", "files", "anki1", "collection.anki2")
            for format in self.mnemosyne.component_manager.all("file_format"):
                if format.__class__.__name__ == "Anki2":
                    format.do_import(filename)
            self.mnemosyne.controller().save_file()
            card = self.mnemosyne.database().card("1502277582871", is_id_internal=False)
            assert card.next_rep == 1503021600

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.fill_server_database = fill_server_database
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.do_sync(); assert last_error is None

        assert self.client.database.card_count() == 7
        assert self.client.database.fact_count() == 6

        card = self.client.database.card("1502277582871", is_id_internal=False)
        assert "img src=\"al.png\"" in card.question(render_chain="plain_text")
        assert self.client.mnemosyne.config().card_type_property(\
                "font", card.card_type, "0") == \
                   "Algerian,23,-1,5,50,0,0,0,0,0,Regular"
        assert card.next_rep == 1503021600
        assert card.last_rep == card.next_rep - 3 * 86400

        card = self.client.database.card("1502277594395", is_id_internal=False)
        assert "audio src=\"1.mp3\"" in card.question(render_chain="plain_text")

        card = self.client.database.card("1502277686022", is_id_internal=False)
        assert "<$$>x</$$>&nbsp;<latex>x^2</latex>&nbsp;<$>x^3</$>" in\
                   card.question(render_chain="plain_text")

        card = self.client.database.card("1502797276041", is_id_internal=False)
        assert "aa <span class=cloze>[...]</span> cc" in\
                   card.question(render_chain="plain_text")
        assert "aa <span class=cloze>bbb</span> cc" in\
                   card.answer(render_chain="plain_text")

        card = self.client.database.card("1502797276050", is_id_internal=False)
        assert "aa bbb <span class=cloze>[...]</span>" in\
                   card.question(render_chain="plain_text")
        assert "aa bbb <span class=cloze>cc</span>" in\
                   card.answer(render_chain="plain_text")
        assert card.next_rep == -1
        assert card.last_rep == -1

        card = self.client.database.card("1502970432696", is_id_internal=False)
        assert "type answer" in\
                   card.question(render_chain="plain_text")
        assert "{{type:Back}}" not in\
                   card.question(render_chain="plain_text")
        assert card.next_rep == 1502970472
        assert card.last_rep == 1502970472

        card = self.client.database.card("1503047582690", is_id_internal=False)
        assert "subdeck card" in\
                   card.question(render_chain="plain_text")
        assert card.next_rep == -1
        assert card.last_rep == -1
        assert card.easiness == 2.5

        criterion = self.client.database.criterion(id=2, is_id_internal=True)
        assert criterion.data_to_string() == "(set(), {2}, set())"
        assert criterion.name == "Deck 1"
        assert len(list(self.client.database.criteria())) == 3

    def test_mem_import(self):

        def fill_server_database(self):
            filename = os.path.join(os.getcwd(), "tests", "files", "1sided.mem")
            for format in self.mnemosyne.component_manager.all("file_format"):
                if format.__class__.__name__ == "Mnemosyne1Mem":
                    format.do_import(filename)
            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.fill_server_database = fill_server_database
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.do_sync(); assert last_error is None

        card = self.client.database.card("9cff728f", is_id_internal=False)
        assert card.grade == 2
        assert card.easiness == 2.5
        assert card.acq_reps == 1
        assert card.ret_reps == 0
        assert card.lapses == 0
        assert card.acq_reps_since_lapse == 1
        assert card.ret_reps_since_lapse == 0
        assert [tag.name for tag in card.tags] == ["__UNTAGGED__"]
        assert card.last_rep == 1247529600
        assert card.next_rep == 1247616000
        assert card.id == "9cff728f"

    def test_mem_import_xml(self):

        def fill_server_database(self):
            filename = os.path.join(os.getcwd(), "tests", "files",
                                    "basedir_2_mem", "deck1.mem")
            for format in self.mnemosyne.component_manager.all("file_format"):
                if format.__class__.__name__ == "Mnemosyne1Mem":
                    format.do_import(filename)
            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer(binary_download=False)
        self.server.fill_server_database = fill_server_database
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.do_sync(); assert last_error is None

        assert self.client.database.con.execute(\
            "select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] != 0
        card = self.client.database.card("0c3f0613", is_id_internal=False)

        assert card.last_rep != 0
        assert card.next_rep != 0

    def test_user_id_edit(self):

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.user_id = "new_user_id"
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        assert self.client.mnemosyne.config()["user_id"] == "user_id"
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.config()["user_id"] == "new_user_id"

    def test_bad_password(self):

        def fill_server_database(self):
            fact_data = {"f": "question",
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.password = "wrong"
        global last_error
        self.client.do_sync(); assert last_error is not None
        last_error = None
        assert self.client.database.card_count() == 0

    def test_latex(self):

        def fill_server_database(self):
            fact_data = {"f": "<latex>a^2</latex><$>b^2</$><$$>c^2</$$>",
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().save_file()
            assert card.question().count("file://") == 3
            assert "_media" not in card.question("sync_to_card_only_client")

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()

        self.client.do_sync(); assert last_error is None
        files = [os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "_latex",
            "4db2425ed3a4fabae0f62663e7613555.png"),
                 os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "_latex",
            "ab8ddeb30a66d731e16390ee62ac383c.png"),
                 os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "_latex",
            "ff66949244c3f6a9018230b95bddfe2b.png")]

        for latex_file in files:
            assert os.path.exists(latex_file)
            os.remove(latex_file)

    def test_latex_edit(self):

        def fill_server_database(self):
            fact_data = {"f": "<latex>a^2</latex>",
                         "b": "<latex>c^2</latex>"}
            card_type = self.mnemosyne.card_type_with_id("1")
            self.card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.card.question()
            self.card.answer()
            self.mnemosyne.controller().save_file()
            new_fact_data = {"f": "<latex>b^2</latex>",
                             "b": "<latex>c^2</latex>"}
            self.mnemosyne.controller().edit_card_and_sisters(self.card,
              new_fact_data,  card_type,
            new_tag_names=["default1"], correspondence=[])
            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.do_sync(); assert last_error is None

        card = self.client.database.card(self.server.card.id, is_id_internal=False)
        assert len(card.tags) == 1
        assert list(card.tags)[0].name == "default1"

        assert self.client.database.con.execute("select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 3

    def test_binary_download(self):

        def fill_server_database(self):
            fact_data = {"f": "<latex>a^2</latex>",
                         "b": "<latex>c^2</latex>"}
            card_type = self.mnemosyne.card_type_with_id("1")
            self.card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.card.question()
            self.card.answer()
            self.mnemosyne.controller().save_file()
            new_fact_data = {"f": "<latex>b^2</latex>",
                             "b": "<latex>c^2</latex>"}
            self.mnemosyne.controller().edit_card_and_sisters(self.card,
              new_fact_data, card_type, new_tag_names=["default1"],
              correspondence=[])
            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer(binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.do_sync(); assert last_error is None

        card = self.client.database.card(self.server.card.id, is_id_internal=False)
        assert len(card.tags) == 1
        assert list(card.tags)[0].name == "default1"

        assert self.client.database.con.execute("select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 3

    def test_binary_download_behind_proxy(self):

        def fill_server_database(self):
            fact_data = {"f": "<latex>a^2</latex>",
                         "b": "<latex>c^2</latex>"}
            card_type = self.mnemosyne.card_type_with_id("1")
            self.card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.card.question()
            self.card.answer()
            self.mnemosyne.controller().save_file()
            new_fact_data = {"f": "<latex>b^2</latex>",
                             "b": "<latex>c^2</latex>"}
            self.mnemosyne.controller().edit_card_and_sisters(self.card,
              new_fact_data, card_type,
            new_tag_names=["default1"], correspondence=[])
            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer(binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.behind_proxy = True
        self.client.do_sync(); assert last_error is None

        card = self.client.database.card(self.server.card.id, is_id_internal=False)
        assert len(card.tags) == 1
        assert list(card.tags)[0].name == "default1"

        assert self.client.database.con.execute("select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 3

    def test_binary_download_no_old_reps(self):

        def fill_server_database(self):
            fact_data = {"f": "<latex>a^2</latex>",
                         "b": "<latex>c^2</latex>"}
            card_type = self.mnemosyne.card_type_with_id("1")
            self.card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.card.question()
            self.card.answer()
            self.mnemosyne.review_controller().learning_ahead = True
            self.mnemosyne.review_controller().show_new_question()
            self.mnemosyne.review_controller().grade_answer(5)
            self.mnemosyne.controller().save_file()
            new_fact_data = {"f": "<latex>b^2</latex>",
                             "b": "<latex>c^2</latex>"}
            self.mnemosyne.controller().edit_card_and_sisters(self.card,
              new_fact_data, card_type,
            new_tag_names=["default1"], correspondence=[])
            self.mnemosyne.controller().save_file()

        def test_server(self):
            assert self.mnemosyne.database().con.execute(\
                "select count() from log where event_type=?",
                (EventTypes.REPETITION, )).fetchone()[0] == 2

        self.server = MyServer(binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.interested_in_old_reps = False
        self.client.do_sync(); assert last_error is None

        card = self.client.database.card(self.server.card.id, is_id_internal=False)
        assert len(card.tags) == 1
        assert list(card.tags)[0].name == "default1"

        assert self.client.database.con.execute("select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 3

        assert self.client.database.con.execute("select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 0

    def test_binary_download_no_pregenerated_data(self):

        def fill_server_database(self):
            fact_data = {"f": "a^2",
                         "b": "b^2"}
            card_type = self.mnemosyne.card_type_with_id("1")
            self.card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

        def test_server(self):
            self.mnemosyne.database().con.execute("select question from cards where id=?",
                                      (self.card.id, )).fetchone()

        self.server = MyServer(binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.store_pregenerated_data = False
        self.client.do_sync(); assert last_error is None

        card = self.client.database.card(self.server.card.id, is_id_internal=False)
        assert len(card.tags) == 2
        try:
            self.client.database.con.execute("select question from cards where id=?",
                                             (self.server.card.id, )).fetchone()
        except:
            pass

    def test_xml_download_no_old_reps(self):

        def fill_server_database(self):
            fact_data = {"f": "<latex>a^2</latex>",
                         "b": "<latex>c^2</latex>"}
            card_type = self.mnemosyne.card_type_with_id("1")
            self.card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.card.question()
            self.card.answer()
            self.mnemosyne.review_controller().learning_ahead = True
            self.mnemosyne.review_controller().show_new_question()
            self.mnemosyne.review_controller().grade_answer(5)
            self.mnemosyne.controller().save_file()
            new_fact_data = {"f": "<latex>b^2</latex>",
                             "b": "<latex>c^2</latex>"}
            self.mnemosyne.controller().edit_card_and_sisters(self.card,
              new_fact_data, card_type,
            new_tag_names=["default1"], correspondence=[])
            self.mnemosyne.controller().save_file()

        def test_server(self):
            assert self.mnemosyne.database().con.execute(\
                "select count() from log where event_type=?",
                (EventTypes.REPETITION, )).fetchone()[0] == 2

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.interested_in_old_reps = False
        self.client.do_sync(); assert last_error is None

        card = self.client.database.card(self.server.card.id, is_id_internal=False)
        assert len(card.tags) == 1
        assert list(card.tags)[0].name == "default1"

        assert self.client.database.con.execute("select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA_FILE, )).fetchone()[0] == 3

        assert self.client.database.con.execute("select count() from log where event_type=?",
            (EventTypes.REPETITION, )).fetchone()[0] == 0

    def test_unicode_database_name(self):

        def test_server(self):
            db = self.mnemosyne.database()
            tag = db.get_or_create_tag_with_name(chr(0x628) + '>&<abcd')
            assert tag.id == self.client_tag_id
            assert tag.name == chr(0x628) + ">&<abcd"
            sql_res = db.con.execute("select timestamp from log where event_type=?",
               (EventTypes.ADDED_TAG, )).fetchone()
            assert self.tag_added_timestamp == sql_res[0]
            assert type(sql_res[0]) == int
            assert db.con.execute("select count() from log").fetchone()[0] == 23

        self.server = MyServer(filename=chr(0x628) + ".db")
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient(filename=chr(0x628) + ".db")
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name(chr(0x628) + ">&<abcd")
        self.server.client_tag_id = tag.id
        sql_res = self.client.mnemosyne.database().con.execute(\
            "select timestamp from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()
        self.server.tag_added_timestamp = sql_res[0]
        assert type(self.server.tag_added_timestamp) == int
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()[0] == 1
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 23

    def test_dont_upload_science_logs(self):

        def fill_server_database(self):
            self.mnemosyne.config()["upload_science_logs"] = True
            fact_data = {"f": "a^2",
                         "b": "c^2"}
            card_type = self.mnemosyne.card_type_with_id("1")
            self.card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["my_tag"])[0]
            self.mnemosyne.review_controller().learning_ahead = True
            self.mnemosyne.review_controller().show_new_question()
            self.mnemosyne.review_controller().grade_answer(5)
            self.mnemosyne.controller().save_file()

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from log where event_type=?",
               (EventTypes.REPETITION, )).fetchone()[0] == 3
            db.dump_to_science_log()
            f = open(os.path.join(os.path.abspath("dot_sync_server"), "log.txt"))
            assert len(f.readlines()) == 27

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.interested_in_old_reps = False
        self.client.upload_science_logs = False
        self.client.mnemosyne.config()["upload_science_logs"] = False
        fact_data = {"f": "a^2",
                     "b": "b^2"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        self.card = self.client.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["my_tag"])[0]
        self.client.mnemosyne.controller().save_file()
        self.i = self.client.database.con.execute(\
            "select _last_log_id from partnerships where partner=?",
            ("log.txt", )).fetchone()[0]
        self.client.do_sync(); assert last_error is None
        self.client.database.dump_to_science_log()

        db = self.client.database
        assert db.con.execute("select count() from log where event_type=?",
               (EventTypes.REPETITION, )).fetchone()[0] == 1
        assert self.i < self.client.database.con.execute(\
            "select _last_log_id from partnerships where partner=?",
            ("log.txt", )).fetchone()[0]
        assert not os.path.exists(os.path.join(os.path.abspath("dot_sync_client"), "log.txt"))

    def test_do_upload_science_logs(self):

        def fill_server_database(self):
            self.mnemosyne.config()["upload_science_logs"] = True
            fact_data = {"f": "a^2",
                         "b": "c^2"}
            card_type = self.mnemosyne.card_type_with_id("1")
            self.card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["my_tag"])[0]
            self.mnemosyne.review_controller().learning_ahead = True
            self.mnemosyne.review_controller().show_new_question()
            self.mnemosyne.review_controller().grade_answer(5)
            self.mnemosyne.controller().save_file()

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from log where event_type=?",
               (EventTypes.REPETITION, )).fetchone()[0] == 3
            db.dump_to_science_log()
            f = open(os.path.join(os.path.abspath("dot_sync_server"), "log.txt"))
            assert len(f.readlines()) == 14

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.interested_in_old_reps = False
        self.client.upload_science_logs = True
        self.client.mnemosyne.config()["upload_science_logs"] = True
        fact_data = {"f": "a^2",
                     "b": "b^2"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        self.card = self.client.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["my_tag"])[0]
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.database.dump_to_science_log()
        assert self.client.database.con.execute(\
            "select _last_log_id from partnerships where partner=?",
            ("log.txt", )).fetchone()[0] != 0
        db = self.client.database
        assert db.con.execute("select count() from log where event_type=?",
               (EventTypes.REPETITION, )).fetchone()[0] == 1
        f = open(os.path.join(os.path.abspath("dot_sync_client"), "log.txt"))

        assert len(f.readlines()) == 6+7

    def test_sync_cycle(self):

        global last_error
        last_error = None

        # A --> B

        def test_server(self):
            pass

        self.server = MyServer(os.path.abspath("dot_sync_B"))
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient(os.path.abspath("dot_sync_A"))
        fact_data = {"f": "a^2",
                     "b": "b^2"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        self.card = self.client.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["my_tag"])[0]
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # B --> C

        def test_server(self):
            pass

        self.server = MyServer(os.path.abspath("dot_sync_C"))
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient(os.path.abspath("dot_sync_B"), erase_previous=False)
        self.client.mnemosyne.review_controller().reset()
        self.client.mnemosyne.review_controller().learning_ahead = True
        self.client.mnemosyne.review_controller().show_new_question()
        self.client.mnemosyne.review_controller().grade_answer(5)
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # C --> A

        def test_server(self):
            pass

        self.server = MyServer(os.path.abspath("dot_sync_A"), erase_previous=False)
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient(os.path.abspath("dot_sync_C"), erase_previous=False)
        self.client.mnemosyne.review_controller().reset()
        self.client.mnemosyne.review_controller().learning_ahead = True
        self.client.mnemosyne.review_controller().show_new_question()
        self.client.mnemosyne.review_controller().grade_answer(5)
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is not None
        assert "cycle" in last_error
        last_error = None

    def test_conflict_cancel(self):

        # First sync.

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.binary_upload = True
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            tag.name = "server"
            self.mnemosyne.database().update_tag(tag)
            self.mnemosyne.database().save()

        def test_server(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            assert tag.name == "server"

        self.server = MyServer(erase_previous=False)
        self.server.tag_id = tag.id
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.binary_upload = True
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()

        global answer
        answer = 2 # Cancel
        self.client.do_sync(); assert last_error is None
        self.server.stop()
        self._wait_for_server_shutdown()

        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "client"

    def test_conflict_keep_remote_binary(self):

        # First sync.

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.binary_upload = True
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            tag.name = "server"
            self.mnemosyne.database().update_tag(tag)
            self.mnemosyne.database().save()

        def test_server(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            assert tag.name == "server"

            assert self.mnemosyne.config().machine_id() not in \
                   self.mnemosyne.database().partners()
            assert len(self.mnemosyne.database().partners()) == 1

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.tag_id = tag.id
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.binary_upload = True
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()

        global answer
        answer = 1 # keep remote
        self.client.do_sync(); assert last_error is None

        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "server"

        assert self.client.mnemosyne.config().machine_id() not in \
            self.client.mnemosyne.database().partners()
        assert len(self.client.mnemosyne.database().partners()) == 1

    def test_conflict_keep_remote(self):

        # First sync.

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            tag.name = "server"
            self.mnemosyne.database().update_tag(tag)
            self.mnemosyne.database().save()

        def test_server(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            assert tag.name == "server"

            assert self.mnemosyne.config().machine_id() not in \
                   self.mnemosyne.database().partners()
            assert len(self.mnemosyne.database().partners()) == 1

        self.server = MyServer(erase_previous=False)
        self.server.tag_id = tag.id
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.binary_upload = True
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()

        global answer
        answer = 1 # keep remote
        self.client.do_sync(); assert last_error is None

        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "server"

        assert self.client.mnemosyne.config().machine_id() not in \
            self.client.mnemosyne.database().partners()
        assert len(self.client.mnemosyne.database().partners()) == 1

    def test_conflict_cancel_no_old_reps(self):

        # First sync.

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            tag.name = "server"
            self.mnemosyne.database().update_tag(tag)
            self.mnemosyne.database().save()

        def test_server(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            assert tag.name == "server"

            assert self.mnemosyne.config().machine_id() not in \
                   self.mnemosyne.database().partners()
            assert len(self.mnemosyne.database().partners()) == 1

        self.server = MyServer(erase_previous=False)
        self.server.tag_id = tag.id
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.interested_in_old_reps = False
        self.client.binary_upload = False
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()

        global answer
        answer = 1 # cancel
        self.client.do_sync(); assert last_error is None

        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "client"

        assert self.client.mnemosyne.config().machine_id() not in \
            self.client.mnemosyne.database().partners()
        assert len(self.client.mnemosyne.database().partners()) == 1

    def test_conflict_keep_remote_no_old_reps(self):

        # First sync.

        def test_server(self):
            partners = self.mnemosyne.database().partners()
            assert len(partners) == 1
            assert self.mnemosyne.database().last_log_index_synced_for(partners[0]) == 23

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            tag.name = "server"
            self.mnemosyne.database().update_tag(tag)
            self.mnemosyne.database().save()

        def test_server(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            assert tag.name == "server"

            assert self.mnemosyne.config().machine_id() not in \
                   self.mnemosyne.database().partners()
            partners = self.mnemosyne.database().partners()
            assert len(partners) == 1
            assert self.mnemosyne.database().last_log_index_synced_for(partners[0]) > 9

        self.server = MyServer(erase_previous=False)
        self.server.tag_id = tag.id
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.interested_in_old_reps = False
        self.client.binary_upload = False
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()

        global answer
        answer = 0 # keep remote
        self.client.do_sync(); assert last_error is None

        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "server"

        assert self.client.mnemosyne.config().machine_id() not in \
            self.client.mnemosyne.database().partners()
        assert len(self.client.mnemosyne.database().partners()) == 1

    def test_conflict_keep_local_binary(self):

        # First sync.

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.binary_upload = True
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            tag.name = "server"
            self.mnemosyne.database().update_tag(tag)
            self.mnemosyne.database().save()

        def test_server(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            assert tag.name == "client"

            assert self.mnemosyne.config().machine_id() not in \
                   self.mnemosyne.database().partners()
            assert len(self.mnemosyne.database().partners()) == 1

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.tag_id = tag.id
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.binary_upload = True
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()

        global answer
        answer = 0 # keep local
        self.client.do_sync(); assert last_error is None

        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "client"

        assert self.client.mnemosyne.config().machine_id() not in \
            self.client.mnemosyne.database().partners()
        assert len(self.client.mnemosyne.database().partners()) == 1

    def test_conflict_keep_local_binary_behind_proxy(self):

        # First sync.

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.behind_proxy = True
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            tag.name = "server"
            self.mnemosyne.database().update_tag(tag)
            self.mnemosyne.database().save()

        def test_server(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            assert tag.name == "client"

            assert self.mnemosyne.config().machine_id() not in \
                   self.mnemosyne.database().partners()
            assert len(self.mnemosyne.database().partners()) == 1

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.tag_id = tag.id
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.behind_proxy = True
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()
        self.client.binary_upload = True

        global answer
        answer = 0 # keep local
        self.client.do_sync(); assert last_error is None

        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "client"

        assert self.client.mnemosyne.config().machine_id() not in \
            self.client.mnemosyne.database().partners()
        assert len(self.client.mnemosyne.database().partners()) == 1

    def test_conflict_keep_remote_binary_media(self):

        # First sync.

        def fill_server_database(self):
            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b.ogg")
            f = open(filename, "w")
            f.write("B")
            f.close()
            fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Remove media.

        filename = os.path.join(os.path.abspath("dot_sync_client"),
                "default.db_media", "b.ogg")
        os.remove(filename)
        assert not os.path.exists(filename)

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            tag.name = "server"
            self.mnemosyne.database().update_tag(tag)
            self.mnemosyne.database().save()

        def test_server(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            assert tag.name == "server"

            assert self.mnemosyne.config().machine_id() not in \
                   self.mnemosyne.database().partners()
            assert len(self.mnemosyne.database().partners()) == 1

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.tag_id = tag.id
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.binary_upload = True
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()

        global answer
        answer = 1 # keep remote
        self.client.do_sync(); assert last_error is None

        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "server"

        assert self.client.mnemosyne.config().machine_id() not in \
            self.client.mnemosyne.database().partners()
        assert len(self.client.mnemosyne.database().partners()) == 1

        assert os.path.exists(filename)

    def test_conflict_keep_local_binary_media(self):

        # First sync.

        def fill_server_database(self):
            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b.ogg")
            f = open(filename, "w")
            f.write("B")
            f.close()
            fact_data = {"f": "question\n<img src=\"%s\">" % (filename),
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

            self.mnemosyne.controller().save_file()

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Remove media.

        filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b.ogg")
        os.remove(filename)
        assert not os.path.exists(filename)

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            tag.name = "server"
            self.mnemosyne.database().update_tag(tag)
            self.mnemosyne.database().save()

        def test_server(self):
            tag = self.mnemosyne.database().tag(self.tag_id, is_id_internal=False)
            assert tag.name == "client"

            assert self.mnemosyne.config().machine_id() not in \
                   self.mnemosyne.database().partners()
            assert len(self.mnemosyne.database().partners()) == 1

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.tag_id = tag.id
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.binary_upload = True
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()

        global answer
        answer = 0 # keep local
        self.client.do_sync(); assert last_error is None

        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "client"

        assert self.client.mnemosyne.config().machine_id() not in \
            self.client.mnemosyne.database().partners()
        assert len(self.client.mnemosyne.database().partners()) == 1

        assert os.path.exists(filename)

    def test_dangling_session(self):

        # First sync.

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().save_file()
        self.client.put_client_log_entries = lambda x : 1/0
        global last_error
        self.client.do_sync(); assert last_error is not None
        last_error = None
        self.client.mnemosyne.finalise()

        # Second sync.

        self.client = MyClient(erase_previous=False)
        self.client.interested_in_old_reps = False
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        tag.name = "client"
        self.client.mnemosyne.database().update_tag(tag)
        self.client.mnemosyne.database().save()

        self.client.do_sync(); assert last_error is not None
        last_error = None
        tag = self.client.mnemosyne.database().tag(tag.id, is_id_internal=False)
        assert tag.name == "client"

        assert self.client.mnemosyne.config().machine_id() not in \
            self.client.mnemosyne.database().partners()
        assert len(self.client.mnemosyne.database().partners()) == 1

    def test_corrupt_plugin(self):

        def fill_server_database(self):
            # Artificially mutilate plugin.
            for plugin in self.mnemosyne.plugins():
                component = plugin.components[0]
                if component.component_type == "card_type" and component.id == "5":
                    plugin.deactivate()
                    plugin.activate = lambda x : 1/0
                    break

        def test_server(self):
            assert self.mnemosyne.database().card_count() == 0
            assert self.mnemosyne.database().con.\
                   execute("select count() from partnerships").fetchone()[0] == 1

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()

        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin
        for plugin in self.client.mnemosyne.plugins():
            if isinstance(plugin, ClozePlugin):
                cloze_plugin = plugin
                plugin.activate()
                break

        fact_data = {"text": "[foo]"}
        card_type_1 = self.client.mnemosyne.card_type_with_id("5")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])[0]
        self.client.mnemosyne.controller().save_file()
        global last_error
        self.client.do_sync(); assert last_error is not None
        last_error = None
        assert self.client.mnemosyne.database().con.\
                   execute("select count() from partnerships").fetchone()[0] == 1

    def test_add_tag_and_update_criterion(self):

        def test_server(self):
            db = self.mnemosyne.database()
            criterion = db.criterion(self.criterion_id,
                is_id_internal=False)
            assert criterion.data_to_string() == "(set(), {2, 4}, set())"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()
        global answer
        answer = 0

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_2"])[0]

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.name = "My criterion"
        c._tag_ids_active = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_1")._id])
        self.client.mnemosyne.database().add_criterion(c)
        self.client.mnemosyne.database().set_current_criterion(c)

        fact_data = {"f": "question3",
                     "b": "answer3"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_3"])[0]

        self.server.criterion_id = c.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_forbidden_tag_and_update_criterion(self):

        def test_server(self):
            db = self.mnemosyne.database()
            criterion = db.criterion(self.criterion_id,
                is_id_internal=False)
            assert criterion.data_to_string() == "(set(), {2, 4}, {3})"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()
        global answer
        answer = 0

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_2"])[0]

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.name = "My criterion"
        c._tag_ids_active = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_1")._id])
        c._tag_ids_forbidden = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_2")._id])
        self.client.mnemosyne.database().add_criterion(c)
        self.client.mnemosyne.database().set_current_criterion(c)

        fact_data = {"f": "question3",
                     "b": "answer3"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_3"])[0]

        self.server.criterion_id = c.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_forbidden_tag_and_dont_update_criterion(self):

        def test_server(self):
            db = self.mnemosyne.database()
            criterion = db.criterion(self.criterion_id,
                is_id_internal=False)
            assert criterion.data_to_string() == "(set(), {2}, {3, 4})"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()
        global answer
        answer = 0

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_2"])[0]

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.name = "My criterion"
        c._tag_ids_active = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_1")._id])
        c._tag_ids_forbidden = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_2")._id])
        self.client.mnemosyne.database().add_criterion(c)
        self.client.mnemosyne.database().set_current_criterion(c)

        answer = 1
        fact_data = {"f": "question3",
                     "b": "answer3"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_3"])[0]

        self.server.criterion_id = c.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_tag_and_dont_update_criterion(self):

        def test_server(self):
            db = self.mnemosyne.database()
            criterion = db.criterion(self.criterion_id,
                is_id_internal=False)
            assert criterion.data_to_string() == "(set(), {2}, set())"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()
        global answer
        answer = 1

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_2"])[0]

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.name = "My criterion"
        c._tag_ids_active = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_1")._id])
        self.client.mnemosyne.database().add_criterion(c)
        self.client.mnemosyne.database().set_current_criterion(c)

        fact_data = {"f": "question3",
                     "b": "answer3"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_3"])[0]

        self.server.criterion_id = c.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_card_type_and_update_criterion(self):

        def test_server(self):
            db = self.mnemosyne.database()
            criterion = db.criterion(self.criterion_id,
                is_id_internal=False)
            assert criterion.data_to_string() == "(set(), {2}, set())"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()
        global answer
        answer = 0

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.name = "My criterion"
        c._tag_ids_active = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_1")._id])
        self.client.mnemosyne.database().add_criterion(c)
        self.client.mnemosyne.database().set_current_criterion(c)

        card_type_1 = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "1 cloned")

        fact_data = {"f": "question3",
                     "b": "answer3"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type_1, grade=4, tag_names=["tag_1"])[0]

        self.server.criterion_id = c.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_card_type_and_dont_update_criterion(self):

        def test_server(self):
            db = self.mnemosyne.database()
            criterion = db.criterion(self.criterion_id,
                is_id_internal=False)
            assert criterion.data_to_string() == "({('1::1 cloned', '1::1 cloned.1')}, {2}, set())"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()
        global answer
        answer = 1

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.name = "My criterion"
        c._tag_ids_active = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_1")._id])
        self.client.mnemosyne.database().add_criterion(c)
        self.client.mnemosyne.database().set_current_criterion(c)

        card_type_1 = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "1 cloned")

        fact_data = {"f": "question3",
                     "b": "answer3"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type_1, grade=4, tag_names=["tag_1"])[0]

        self.server.criterion_id = c.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_and_delete_card_type(self):

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        card_type_1 = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "1 cloned snippets")
        self.client.mnemosyne.config().set_card_type_property(\
            "hide_pronunciation_field", True, card_type_1)
        self.client.mnemosyne.controller().delete_card_type(card_type_1)

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_criterion(self):

        def test_server(self):
            db = self.mnemosyne.database()
            criterion = db.criterion(self.criterion_id,
                is_id_internal=False)
            assert criterion.data_to_string() == "({('5', '5.1')}, {3}, {4})"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin
        for plugin in self.client.mnemosyne.plugins():
            if isinstance(plugin, ClozePlugin):
                cloze_plugin = plugin
                plugin.activate()
                break

        fact_data = {"text": "[foo]"}
        card_type_1 = self.client.mnemosyne.card_type_with_id("5")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])[0]

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_2"])[0]

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.name = "My criterion"
        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_1.id, card_type_1.fact_views[0].id)])
        c._tag_ids_active = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_1")._id])
        c._tag_ids_forbidden = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_2")._id])
        self.client.mnemosyne.database().add_criterion(c)
        self.client.mnemosyne.database().set_current_criterion(c)

        self.server.criterion_id = c.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_edit_criterion(self):

        def test_server(self):
            db = self.mnemosyne.database()
            criterion = db.criterion(self.criterion_id,
                is_id_internal=False)
            print (criterion.data_to_string())
            assert criterion.data_to_string() == "({('5', '5.1')}, {3}, set())"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin
        for plugin in self.client.mnemosyne.plugins():
            if isinstance(plugin, ClozePlugin):
                cloze_plugin = plugin
                plugin.activate()
                break

        fact_data = {"text": "[foo]"}
        card_type_1 = self.client.mnemosyne.card_type_with_id("5")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])[0]

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_2"])[0]

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.name = "My criterion"
        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_1.id, card_type_1.fact_views[0].id)])
        c._tag_ids_active = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_1")._id])
        c._tag_ids_forbidden = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_2")._id])
        self.client.mnemosyne.database().add_criterion(c)
        self.client.mnemosyne.database().set_current_criterion(c)

        c._tag_ids_forbidden = set()
        self.client.mnemosyne.database().update_criterion(c)

        self.server.criterion_id = c.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_delete_criterion(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from criteria where id=?",
                (self.criterion_id, )).fetchone()[0] == 0

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin
        for plugin in self.client.mnemosyne.plugins():
            if isinstance(plugin, ClozePlugin):
                cloze_plugin = plugin
                plugin.activate()
                break

        fact_data = {"text": "[foo]"}
        card_type_1 = self.client.mnemosyne.card_type_with_id("5")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type_1,
           grade=-1, tag_names=["default"])[0]

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1"])[0]

        fact_data = {"f": "question2",
                     "b": "answer2"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_2"])[0]

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.name = "My criterion"
        c.deactivated_card_type_fact_view_ids = \
            set([(card_type_1.id, card_type_1.fact_views[0].id)])
        c._tag_ids_active = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_1")._id])
        c._tag_ids_forbidden = set([self.client.mnemosyne.database().\
            get_or_create_tag_with_name("tag_2")._id])
        self.client.mnemosyne.database().add_criterion(c)
        self.client.mnemosyne.database().set_current_criterion(c)
        self.client.mnemosyne.database().delete_criterion(c)
        self.server.criterion_id = c.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_fact_view(self):

        def test_server(self):
            db = self.mnemosyne.database()
            fact_view = db.fact_view(self.fact_view_id,
                is_id_internal=False)
            assert fact_view.id == "1.1"
            assert fact_view.name == "Front-to-back"
            assert fact_view.q_fact_keys == ["f"]
            assert fact_view.a_fact_keys == ["b"]
            assert fact_view.q_fact_key_decorators["f"] == 'question is: $f'
            assert fact_view.a_fact_key_decorators["b"] == 'answer is: $b'
            assert fact_view.a_on_top_of_q == False
            assert type(fact_view.a_on_top_of_q) == type(False)
            assert fact_view.type_answer == False
            assert type(fact_view.type_answer) == type(False)
            assert fact_view.extra_data["1"] == 2

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        card_type = self.client.mnemosyne.card_type_with_id("1")

        fact_view = card_type.fact_views[0]
        fact_view.q_fact_key_decorators = {"f": 'question is: $f'}
        fact_view.a_fact_key_decorators = {"b": 'answer is: $b'}
        fact_view.extra_data = {'1': 2}
        self.client.mnemosyne.database().add_fact_view(fact_view)

        self.server.fact_view_id = fact_view.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

        fact_view.q_fact_key_decorators = {}
        fact_view.a_fact_key_decorators = {}

    def test_edit_fact_view(self):

        def test_server(self):
            db = self.mnemosyne.database()
            fact_view = db.fact_view(self.fact_view_id,
                is_id_internal=False)
            assert fact_view.extra_data["1"] == 3

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        card_type = self.client.mnemosyne.card_type_with_id("1")

        fact_view = card_type.fact_views[0]
        fact_view.extra_data = {'1': 2}
        self.client.mnemosyne.database().add_fact_view(fact_view)

        fact_view.extra_data = {'1': 3}
        self.client.mnemosyne.database().update_fact_view(fact_view)

        self.server.fact_view_id = fact_view.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_delete_fact_view(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from fact_views where id=?",
                (self.fact_view_id, )).fetchone()[0] == 0

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        card_type = self.client.mnemosyne.card_type_with_id("1")

        fact_view = card_type.fact_views[0]
        self.server.fact_view_id = fact_view.id
        fact_view.extra_data = {'1': 2}
        self.client.mnemosyne.database().add_fact_view(fact_view)
        self.client.mnemosyne.database().delete_fact_view(fact_view)

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_card_type(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from fact_views").fetchone()[0] == 1
            card_type = db.card_type(self.card_type_id, is_id_internal=False)
            assert card_type.name == "1 cloned"
            assert card_type.fact_keys_and_names == [("f", 'Front'), ("b", 'Back')]
            assert card_type.unique_fact_keys == ["f"]
            assert card_type.required_fact_keys == ["f"]
            assert card_type.keyboard_shortcuts == {}
            assert len(card_type.fact_views) == 1
            fact_view = card_type.fact_views[0]
            assert fact_view.id == "1::1 cloned.1"
            assert fact_view.name == "Front-to-back"
            assert fact_view.q_fact_keys == ["f"]
            assert fact_view.a_fact_keys == ["b"]
            assert fact_view.a_on_top_of_q == False
            assert type(fact_view.a_on_top_of_q) == type(False)
            assert fact_view.type_answer == False
            assert type(fact_view.type_answer) == type(False)

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        card_type = self.client.mnemosyne.card_type_with_id("1")
        card_type_1 = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "1 cloned")
        self.server.card_type_id = card_type_1.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_add_card_type_needing_plugin(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from fact_views").fetchone()[0] == 1
            card_type = db.card_type(self.card_type_id, is_id_internal=False)
            assert card_type.name == "5 cloned"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        from mnemosyne.libmnemosyne.card_types.cloze import ClozePlugin
        for plugin in self.client.mnemosyne.plugins():
            if isinstance(plugin, ClozePlugin):
                cloze_plugin = plugin
                plugin.activate()
                break

        card_type_1 = self.client.mnemosyne.card_type_with_id("5")

        card_type = self.client.mnemosyne.card_type_with_id("5")
        card_type_1 = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "5 cloned")
        self.server.card_type_id = card_type_1.id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_edit_card_type(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from fact_views").fetchone()[0] == 1
            card_type = db.card_type(self.card_type_id, is_id_internal=False)
            assert card_type.name == "1 cloned"
            assert card_type.fact_keys_and_names == [("f", 'Front'), ("b", 'Back')]
            assert card_type.unique_fact_keys == ["f"]
            assert card_type.required_fact_keys == ["f"]
            assert card_type.keyboard_shortcuts == {}
            assert card_type.extra_data[1] == 1
            assert len(card_type.fact_views) == 1
            fact_view = card_type.fact_views[0]
            assert fact_view.id == "1::1 cloned.1"
            assert fact_view.name == "Front-to-back"
            assert fact_view.q_fact_keys == ["f"]
            assert fact_view.a_fact_keys == ["b"]
            assert fact_view.a_on_top_of_q == False
            assert type(fact_view.a_on_top_of_q) == type(False)
            assert fact_view.type_answer == False
            assert type(fact_view.type_answer) == type(False)

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        card_type = self.client.mnemosyne.card_type_with_id("1")
        card_type_1 = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "1 cloned")
        self.server.card_type_id = card_type_1.id

        card_type_1.extra_data = {1: 1}
        card_type_1 = self.client.mnemosyne.database().update_card_type(card_type_1)

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_delete_card_type(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.con.execute("select count() from card_types where id=?",
                (self.card_type_id, )).fetchone()[0] == 0

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        card_type = self.client.mnemosyne.card_type_with_id("1")
        card_type_1 = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "1 cloned")
        self.server.card_type_id = card_type_1.id

        self.client.mnemosyne.controller().delete_card_type(card_type_1)
        assert self.server.card_type_id not in \
               self.client.mnemosyne.component_manager.card_type_with_id

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_messages(self):
        self.server = None
        self.client = MyClient()

        xml = self.client.text_format.repr_message("message")
        message, traceback = self.client.text_format.parse_message(xml)
        assert message == "message"
        assert traceback == None

        xml = self.client.text_format.repr_message("message", "traceback")
        message, traceback = self.client.text_format.parse_message(xml)
        assert message == "message"
        assert traceback == "traceback"

    def test_reset_database(self):

        global last_error
        last_error = None

        # First sync.

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name(chr(0x628) + ">&<abcd")
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

        self.client.mnemosyne.controller().show_new_file_dialog()

        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        assert last_error == None

        # Second sync.

        def fill_server_database(self):
            tag = self.mnemosyne.database().get_or_create_tag_with_name("tag2")

        def test_server(self):
            assert len(self.mnemosyne.database().tags()) == 3
            assert len(self.mnemosyne.database().partners()) == 1

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(erase_previous=False)
        self.client.do_sync(); assert last_error is None
        assert len(self.client.mnemosyne.database().tags()) == 3
        assert len(self.client.mnemosyne.database().partners()) == 1

    def test_delete_forbidden_tag(self):

        # First sync.

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        card_type = self.client.mnemosyne.card_type_with_id("1")
        fact_data = {"f": "question",  "b": "answer"}
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["forbidden"])[0]
        assert self.client.mnemosyne.database().active_count() == 1

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c.deactivated_card_type_fact_view_ids = set()
        c._tag_ids_active = set([self.client.mnemosyne.database().get_or_create_tag_with_name("active")._id, 1])
        c._tag_ids_forbidden = set([self.client.mnemosyne.database().get_or_create_tag_with_name("forbidden")._id])
        self.client.mnemosyne.database().set_current_criterion(c)
        assert self.client.mnemosyne.database().active_count() == 0

        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            pass

        def test_server(self):
            card = self.mnemosyne.database().card(self.card_id, is_id_internal=False)
            assert card.active == True
            assert self.mnemosyne.database().active_count() == 1

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()
        self.server.card_id = card.id

        self.client = MyClient(erase_previous=False)

        from mnemosyne.libmnemosyne.tag_tree import TagTree
        tree = TagTree(self.client.mnemosyne.component_manager)
        tree.delete_subtree("forbidden")

        self.client.do_sync(); assert last_error is None

        assert self.client.mnemosyne.database().active_count() == 1

    def test_remove_from_queue_after_sync(self):

        # First sync.
        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]

        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            self.mnemosyne.review_controller().learning_ahead = True
            self.mnemosyne.review_controller().show_new_question()
            assert self.mnemosyne.review_controller().card is not None
            self.mnemosyne.review_controller().learning_ahead = False

        def test_server(self):
            self.mnemosyne.review_controller().reset_but_try_to_keep_current_card()
            assert self.mnemosyne.review_controller().card is None

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()
        self.server.card_id = card.id

        self.client = MyClient(erase_previous=False)

        self.client.mnemosyne.review_controller().learning_ahead = True
        self.client.mnemosyne.review_controller().show_new_question()
        self.client.mnemosyne.review_controller().grade_answer(5)
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_remove_from_queue_after_sync_2(self):

        # First sync.
        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]

        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def fill_server_database(self):
            self.mnemosyne.review_controller().learning_ahead = True
            self.mnemosyne.review_controller().show_new_question()
            assert self.mnemosyne.review_controller().card is not None
            self.mnemosyne.review_controller().learning_ahead = False

        def test_server(self):
            self.mnemosyne.review_controller().reset_but_try_to_keep_current_card()
            assert self.mnemosyne.review_controller().card is None

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()
        self.server.card_id = card.id

        self.client = MyClient(erase_previous=False)

        self.client.mnemosyne.database().delete_card(card)
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_convert_card_to_clone(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.card(self.card_id, is_id_internal=False).card_type.id == "1::1 cloned"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]
        self.server.card_id = card.id
        card_type_clone = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "1 cloned")
        self.client.mnemosyne.controller().change_card_type([card.fact],
            card_type, card_type_clone, correspondence={})
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_convert_chain(self):

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type_1 = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type_1,
            grade=-1, tag_names=["a"])[0]
        card_type_2 = self.client.mnemosyne.card_type_with_id("2")
        self.client.mnemosyne.controller().change_card_type([card.fact],
            card_type_1, card_type_2, correspondence={})
        self.client.mnemosyne.controller().change_card_type([card.fact],
            card_type_2, card_type_1, correspondence={})

        from mnemosyne.libmnemosyne.card_types.sentence import SentencePlugin
        for plugin in self.client.mnemosyne.plugins():
            if isinstance(plugin, SentencePlugin):
                plugin.activate()
                break
        card_type = self.client.mnemosyne.card_type_with_id("6")
        card_type_clone = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "6 cloned")
        self.client.mnemosyne.controller().change_card_type([card.fact],
            card_type_1, card_type_clone, correspondence= {"f": "m_1", "b": "f"})
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_convert_card_to_clone_2(self):

        def test_server(self):
            pass

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data, card_type,
            grade=-1, tag_names=["a"])[0]

        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Second sync.

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.card(self.card_id, is_id_internal=False).card_type.id == "1::1 cloned"

        self.server = MyServer(erase_previous=False, binary_download=True)
        self.server.test_server = test_server
        self.server.start()
        self.server.card_id = card.id

        self.client = MyClient(erase_previous=False)

        self.server.card_id = card.id
        card_type_clone = self.client.mnemosyne.controller().clone_card_type(\
            card_type, "1 cloned")
        self.client.mnemosyne.controller().change_card_type([card.fact],
            card_type, card_type_clone, correspondence={})
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_three_partners_untagged(self):

        # client A --> server B

        def test_server(self):
            pass

        self.server = MyServer(os.path.abspath("dot_sync_B"))
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient(os.path.abspath("dot_sync_A"))

        fact_data = {"f": "a^2",
                     "b": "b^2"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        self.card = self.client.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=[])[0]
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # client C --> server B

        def test_server(self):
            assert len(self.mnemosyne.database().tags()) == 1

        self.server = MyServer(os.path.abspath("dot_sync_B"), erase_previous=False)
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient(os.path.abspath("dot_sync_C"))

        self.client.mnemosyne.review_controller().reset()

        fact_data = {"f": "c^2",
                     "b": "d^2"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        self.card = self.client.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=[])[0]
        self.client.mnemosyne.controller().save_file()

        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().fact_count() == 2

    def test_sync_current_criterion(self):

        def test_server(self):
            assert self.mnemosyne.database().active_count() == 0

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=[])[0]

        assert self.client.mnemosyne.database().active_count() == 1

        c = DefaultCriterion(self.client.mnemosyne.component_manager)
        c._tag_ids_active = set([1])
        c._tag_ids_forbidden = set([1])
        self.client.mnemosyne.database().set_current_criterion(c)
        assert self.client.mnemosyne.database().active_count() == 0

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_setting(self):

        def test_server(self):
            assert self.mnemosyne.config()["font"]["1"]["f"] == \
                   "my_font,12,x,x,25,2,1,1,x,x"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        # Make sure database is not empty, otherwise we copy over the server
        # database as initial sync.

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

        self.client.mnemosyne.config()["font"] = {}
        self.client.mnemosyne.config()["font"]["1"] = {}
        self.client.mnemosyne.config()["font"]["1"]["f"] = "my_font,12,x,x,25,2,1,1,x,x"

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_setting_2(self):

        def fill_server_database(self):
            self.mnemosyne.config().keys_to_sync.remove("font")

        def test_server(self):
            assert "1" not in self.mnemosyne.config()["font"]
            assert self.mnemosyne.database().con.execute(\
                "select count() from log where event_type=?",
                (EventTypes.EDITED_SETTING, )).fetchone()[0] == 1

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()

        # Make sure database is not empty, otherwise we copy over the server
        # database as initial sync.

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

        self.client.mnemosyne.config()["font"] = {}
        self.client.mnemosyne.config()["font"]["1"] = {}
        self.client.mnemosyne.config()["font"]["1"]["f"] = "my_font,12,x,x,25,2,1,1,x,x"

        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_setting_3(self):

        def test_server(self):
            pass

        def fill_server_database(self):
            fact_data = {"f": "question",
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.config()["font"] = {}
            self.mnemosyne.config()["font"]["1"] = {}
            self.mnemosyne.config()["font"]["1"]["f"] = "my_font,12,x,x,25,2,1,1,x,x"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.do_sync(); assert last_error is None

        assert self.client.mnemosyne.config()["font"]["1"]["f"] == \
               "my_font,12,x,x,25,2,1,1,x,x"

    def test_setting_4(self):

        def test_server(self):
            pass

        def fill_server_database(self):
            fact_data = {"f": "question",
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.config()["font"] = {}
            self.mnemosyne.config()["font"]["1"] = {}
            self.mnemosyne.config()["font"]["1"]["f"] = "my_font,12,x,x,25,2,1,1,x,x"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.mnemosyne.config().keys_to_sync.remove("font")
        self.client.do_sync(); assert last_error is None

        assert "1" not in self.client.mnemosyne.config()["font"]
        db = self.client.database
        assert db.con.execute("select count() from log where event_type=?",
               (EventTypes.EDITED_SETTING, )).fetchone()[0] == 21

    def test_setting_5(self):

        def test_server(self):
            assert self.mnemosyne.config().card_type_property("font",
                self.mnemosyne.card_type_with_id("1"), "f") == \
                   "my_font,12,x,x,25,2,1,1,x,x"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()

        # Make sure database is not empty, otherwise we copy over the server
        # database as initial sync.

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

        self.client.mnemosyne.config().set_card_type_property\
            ("font", "my_font,12,x,x,25,2,1,1,x,x", card_type)
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_binary_sync_setting_1(self):

        def test_server(self):
            assert self.mnemosyne.config().card_type_property("font",
                self.mnemosyne.card_type_with_id("1"), "f") \
                   == "my_font,12,x,x,25,2,1,1,x,x"

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        self.client.binary_upload = True

        # Make sure database is not empty, otherwise we copy over the server
        # database as initial sync.

        fact_data = {"f": "question",
                     "b": "answer"}
        card_type = self.client.mnemosyne.card_type_with_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]

        self.client.mnemosyne.config().set_card_type_property\
            ("font", "my_font,12,x,x,25,2,1,1,x,x", card_type)
        self.client.mnemosyne.controller().save_file()
        self.client.do_sync(); assert last_error is None

    def test_binary_sync_setting_2(self):

        def test_server(self):
            pass

        def fill_server_database(self):
            fact_data = {"f": "question",
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.config()["font"] = {}
            self.mnemosyne.config()["font"]["1"] = {}
            self.mnemosyne.config()["font"]["1"]["f"] = "my_font,12,x,x,25,2,1,1,x,x"

        self.server = MyServer(binary_download=True)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.do_sync(); assert last_error is None

        assert self.client.mnemosyne.config()["font"]["1"]["f"] == \
               "my_font,12,x,x,25,2,1,1,x,x"

    def test_restore_backup(self):

        # Sync 1.

        def test_server(self):
            pass

        def fill_server_database(self):
            fact_data = {"f": "question",
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=[])[0]

        self.server = MyServer(os.path.abspath("dot_sync_server"))
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(os.path.abspath("dot_sync_client"))
        self.client.do_sync(); assert last_error is None
        self.client.database.save(os.path.join(os.path.abspath("dot_sync_client"), "backup.db"))
        assert self.client.mnemosyne.database().fact_count() == 1
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Sync 2.

        def test_server(self):
            pass

        def fill_server_database(self):
            fact_data = {"f": "question2",
                         "b": "answer2"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=[])[0]

        self.server = MyServer(os.path.abspath("dot_sync_server"), erase_previous=False)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(os.path.abspath("dot_sync_client"), erase_previous=False)
        self.client.binary_upload = True
        self.client.do_sync(); assert last_error is None
        self.client.database.restore(os.path.join(os.path.abspath("dot_sync_client"), "backup.db"))
        assert self.client.mnemosyne.database().fact_count() == 1
        global answer
        answer = 1 # keep remote
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().fact_count() == 2

    def test_restore_backup_2(self):

        # Sync 1.

        def test_server(self):
            pass

        def fill_server_database(self):
            fact_data = {"f": "question",
                         "b": "answer"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=[])[0]

        self.server = MyServer(os.path.abspath("dot_sync_server"))
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(os.path.abspath("dot_sync_client"))
        self.client.do_sync(); assert last_error is None
        self.client.mnemosyne.finalise()
        self.server.stop()
        self._wait_for_server_shutdown()

        # Sync 2.

        def test_server(self):
            pass

        def fill_server_database(self):
            old_path = self.mnemosyne.config()["last_database"]
            self.mnemosyne.database().save(\
                os.path.join(os.path.abspath("dot_sync_server"), "backup.db"))
            self.mnemosyne.config()["last_database"] = old_path
            fact_data = {"f": "question2",
                         "b": "answer2"}
            card_type = self.mnemosyne.card_type_with_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=[])[0]
            assert self.mnemosyne.database().fact_count() == 2
            self.mnemosyne.database().restore(os.path.join(\
                os.path.abspath("dot_sync_server"), "backup.db"))
            assert self.mnemosyne.database().fact_count() == 1

        self.server = MyServer(os.path.abspath("dot_sync_server"),
            filename="default.db", erase_previous=False)
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient(os.path.abspath("dot_sync_client"),
            filename="default.db", erase_previous=False)
        global answer
        answer = 0 # keep local
        self.client.do_sync(); assert last_error is None
        assert self.client.mnemosyne.database().fact_count() == 1

    def test_upload_archive(self):

        def test_server(self):
            assert self.client_archive_names == os.listdir(self.archive_path)

        def fill_server_database(self):
            self.archive_path = os.path.join(os.getcwd(), "dot_sync_server", "archive")
            if os.path.exists(self.archive_path):
                shutil.rmtree(self.archive_path)

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()


        # This is a throwaway variable to deal with a python bug
        import datetime
        throwaway = datetime.datetime.strptime('20110101','%Y%m%d')


        self.client = MyClient()
        self.client.binary_upload = True

        # Import old history.
        filename = os.path.join(os.getcwd(), "tests", "files", "basedir_bz2",
                                "default.mem")
        mem_importer = None
        for format in self.client.mnemosyne.component_manager.all("file_format"):
            if format.__class__.__name__ == "Mnemosyne1Mem":
                mem_importer = format
                break
        mem_importer.do_import(filename)
        self.client.mnemosyne.database().archive_old_logs()

        archive_path = os.path.join(os.getcwd(), "dot_sync_client", "archive")
        self.server.client_archive_names = os.listdir(archive_path)

        self.client.do_sync(); assert last_error is None

    def test_download_archive(self):

        def test_server(self):
            pass

        def fill_server_database(self):
            # Import old history.
            filename = os.path.join(os.getcwd(), "tests", "files", "basedir_bz2",
                                "default.mem")
            mem_importer = None
            for format in self.mnemosyne.component_manager.all("file_format"):
                if format.__class__.__name__ == "Mnemosyne1Mem":
                    mem_importer = format
                    break
            mem_importer.do_import(filename)
            self.mnemosyne.database().archive_old_logs()

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()

        self.client = MyClient()
        self.client.binary_upload = True

        client_archive_path = os.path.join(os.getcwd(), "dot_sync_client", "archive")
        if os.path.exists(client_archive_path):
            shutil.rmtree(client_archive_path)

        self.client.do_sync(); assert last_error is None

        client_archive_names = os.listdir(client_archive_path)

        server_archive_path = os.path.join(os.getcwd(), "dot_sync_server", "archive")
        server_archive_names = os.listdir(server_archive_path)

        assert client_archive_names == server_archive_names
