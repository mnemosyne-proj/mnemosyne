#
# test_sync.py <Peter.Bienstman@UGent.be>
#

import os
from nose.tools import raises
from threading import Thread, Lock

from openSM2sync.server import Server
from openSM2sync.client import Client
from openSM2sync.log_entry import EventTypes

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

server_lock = Lock()

class Widget(MainWidget):
    
    def status_bar_message(self, message):
        print message
        
    def information_box(self, info):
        print info
        
    def error_box(self, error):
        print error

        
class MyServer(Server, Thread):

    program_name = "Mnemosyne"
    program_version = "test"

    user_id = "user_id"

    stop_after_sync = True

    def __init__(self):
        Thread.__init__(self)
        os.system("rm -fr dot_sync_server")
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("test_sync", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ProgressDialog"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
     
    def authorise(self, login, password):
        return login == "user" and password == "pass"

    def open_database(self, database_name):
        return self.mnemosyne.database()

    def run(self):
        # We only open the database connection inside the thread to prevent
        # access problems, as a single connection can only be used inside a
        # single thread.
        # We use a lock here to prevent the client from accessing the server
        # until the server is ready.
        global server_lock
        server_lock.acquire()
        self.mnemosyne.initialise(os.path.abspath("dot_sync_server"))
        self.mnemosyne.config().change_user_id(self.user_id)
        self.mnemosyne.review_controller().reset()
        if hasattr(self, "fill_server_database"):
            self.fill_server_database(self)
        Server.__init__(self, "server_machine_id", "127.0.0.1", 9164,
                        self.mnemosyne.main_widget())
        self.supports_binary_log_download = lambda x,y : False
        server_lock.release()
        # Because we stop_after_sync is True, serve_forever will actually stop
        # after one sync.
        self.serve_forever()
        # Also running the actual tests we need to do inside this thread and
        # not in the main thread, again because of sqlite access restrictions.
        # However, if the asserts fail in this thread, nose won't flag them as
        # failures in the main thread, so we communicate failure back to the
        # main thread using self.passed_tests.
        self.passed_tests = False
        self.test_server(self)
        self.passed_tests = True
        self.mnemosyne.finalise()


class MyClient(Client):
    
    program_name = "Mnemosyne"
    program_version = "test"
    capabilities = "mnemosyne_dynamic_cards"
    user = "user"
    password = "pass"
    
    def __init__(self):
        os.system("rm -fr dot_sync_client")
        self.mnemosyne = Mnemosyne()
        self.mnemosyne.components.insert(0, ("mnemosyne.libmnemosyne.translator",
                             "GetTextTranslator"))
        self.mnemosyne.components.append(("test_sync", "Widget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.review_widget", "ReviewWidget"))
        self.mnemosyne.components.append(\
            ("mnemosyne.libmnemosyne.ui_components.dialogs", "ProgressDialog"))
        self.mnemosyne.initialise(os.path.abspath(os.path.join(os.getcwdu(),
                                  "dot_sync_client")))
        self.mnemosyne.config().change_user_id("user_id")
        self.mnemosyne.review_controller().reset()        
        Client.__init__(self, "client_machine_id", self.mnemosyne.database(),
                        self.mnemosyne.main_widget())
        
    def do_sync(self):
        global server_lock
        server_lock.acquire()
        self.sync("127.0.0.1", 9164, self.user, self.password)
        server_lock.release()


class TestSync(object):

    def teardown(self):
        self.client.mnemosyne.finalise()
        assert self.server.passed_tests == True
        
    def test_add_tag(self):

        def test_server(self):
            db = self.mnemosyne.database()
            tag = db.get_or_create_tag_with_name(unichr(0x628) + u'>&<abcd')
            assert tag.id == self.client_tag_id
            assert tag.name == unichr(0x628) + u">&<abcd"
            sql_res = db.con.execute("select * from log where event_type=?",
               (EventTypes.ADDED_TAG, )).fetchone()
            assert self.tag_added_timestamp == sql_res["timestamp"]
            assert type(sql_res["timestamp"]) == int
            assert db.con.execute("select count() from log").fetchone()[0] == 8 
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name(unichr(0x628) + u">&<abcd")
        self.server.client_tag_id = tag.id
        sql_res = self.client.mnemosyne.database().con.execute(\
            "select * from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()
        self.server.tag_added_timestamp = sql_res["timestamp"]
        assert type(self.server.tag_added_timestamp) == int
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log where event_type=?", (EventTypes.ADDED_TAG,
             )).fetchone()[0] == 1
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 8

    def test_update_tag(self):
 
        def test_server(self):
            db = self.mnemosyne.database()
            tag = db.get_tag(self.client_tag_id, id_is_internal=False)
            assert tag.extra_data["A"] == "<a>"
            assert db.con.execute("select count() from log").\
                   fetchone()[0] == 9
        
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name("tag")
        tag.extra_data = {"A": "<a>"}
        self.client.mnemosyne.database().update_tag(tag)
        self.server.client_tag_id = tag.id
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 9
        
    def test_delete_tag(self):
        def test_server(self):
            db = self.mnemosyne.database()
            try:
                tag = db.get_tag(self.client_tag_id, id_is_internal=False)
                assert 1 == 0
            except TypeError:
                pass
            assert db.con.execute("select count() from log").\
                   fetchone()[0] == 10
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        tag = self.client.mnemosyne.database().\
              get_or_create_tag_with_name("tag")
        self.client.mnemosyne.controller().file_save()
        self.client.mnemosyne.database().delete_tag(tag)
        self.server.client_tag_id = tag.id
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
                "select count() from log").fetchone()[0] == 10

    def test_add_fact(self):

        def test_server(self):
            db = self.mnemosyne.database()
            fact = db.get_fact(self.client_fact_id, id_is_internal=False)
            assert fact.data == {"q": "Q", "a": ""}
            assert fact.card_type == self.mnemosyne.card_type_by_id("1")
            assert fact.creation_time == self.client_creation_time
            assert fact.modification_time == self.client_creation_time
            assert db.con.execute("select count() from log").fetchone()[0] == 8 
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        card_type = self.client.mnemosyne.card_type_by_id("1")
        fact = Fact({"q": "Q", "a": ""}, card_type)
        self.client.mnemosyne.database().add_fact(fact)
        self.server.client_fact_id = fact.id
        self.server.client_creation_time = fact.creation_time
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 8
        
    def test_update_fact(self):

        def test_server(self):
            db = self.mnemosyne.database()
            fact = db.get_fact(self.client_fact_id, id_is_internal=False)
            assert fact.data == {"q": "Q", "a": "AA"}
            assert fact.card_type == self.mnemosyne.card_type_by_id("1")
            assert fact.creation_time == self.client_creation_time
            assert fact.modification_time == self.client_creation_time
            assert db.con.execute("select count() from log").fetchone()[0] == 9
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        card_type = self.client.mnemosyne.card_type_by_id("1")
        fact = Fact({"q": "Q", "a": "A"}, card_type)
        self.client.mnemosyne.database().add_fact(fact)
        fact.data = {"q": "Q", "a": "AA"}
        self.client.mnemosyne.database().update_fact(fact)        
        self.server.client_fact_id = fact.id
        self.server.client_creation_time = fact.creation_time
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 9
        
    def test_delete_fact(self):

        def test_server(self):
            db = self.mnemosyne.database()
            try:
                fact = db.get_fact(self.client_fact_id, id_is_internal=False)
                assert 1 == 0
            except TypeError:
                pass
            assert db.con.execute("select count() from log").fetchone()[0] == 11
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        card_type = self.client.mnemosyne.card_type_by_id("1")
        fact = Fact({"q": "Q", "a": "A"}, card_type)
        self.client.mnemosyne.database().add_fact(fact)
        self.client.mnemosyne.controller().file_save()
        self.client.mnemosyne.database().delete_fact_and_related_data(fact)        
        self.server.client_fact_id = fact.id
        self.server.client_creation_time = fact.creation_time
        self.client.mnemosyne.controller().file_save()
        self.client.mnemosyne.log().stopped_program()
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 11
        
    def test_add_cards(self):

        def test_server(self):
            db = self.mnemosyne.database()
            assert db.fact_count() == 1
            assert db.card_count() == 1
            card = db.get_card(self.client_card.id, id_is_internal=False)
            assert card.question() == self.client_card.question()
            tag_ids = [tag.id for tag in card.tags]
            assert db.get_or_create_tag_with_name("tag_1").id in tag_ids
            assert db.get_or_create_tag_with_name("tag_2").id in tag_ids
            assert len(card.tags) == 2
            assert card.scheduler_data == 0
            assert card.active == True
            assert card.in_view == True
            assert card.grade == 4
            assert card.easiness == 2.5
            assert card.acq_reps == 1
            assert card.ret_reps == 0
            assert card.lapses == 0
            assert card.acq_reps_since_lapse == 1
            assert card.ret_reps_since_lapse == 0
            assert card.last_rep != -1
            assert card.next_rep != -1
            assert db.con.execute("select count() from log").fetchone()[0] == 12
            assert card.id == self.client_card.id
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.client.mnemosyne.card_type_by_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.server.client_card = card
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 12

    def test_edit_cards(self):

        def test_server(self):
            db = self.mnemosyne.database()
            card = db.get_card(self.client_card.id, id_is_internal=False)
            assert card.extra_data == {"A": "B"}
            assert db.con.execute("select count() from log").fetchone()[0] == 13
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.client.mnemosyne.card_type_by_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.server.client_card = card
        card.extra_data = {"A": "B"}
        self.client.database.update_card(card)
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 13
            
    def test_delete_cards(self):

        def test_server(self):
            db = self.mnemosyne.database()
            try:
                card = db.get_card(self.client_card.id, id_is_internal=False)
                assert 1 == 0
            except TypeError:
                pass
            assert db.con.execute("select count() from log").fetchone()[0] == 15
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.client.mnemosyne.card_type_by_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.server.client_card = card
        self.client.database.delete_card(card)
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 15

    def test_repetition(self):

        def test_server(self):
            db = self.mnemosyne.database()
            card = db.get_card(self.client_card.id, id_is_internal=False)
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
            assert rep["grade"] == 5
            assert rep["easiness"] == 2.5
            assert rep["acq_reps"] == 1
            assert rep["ret_reps"] == 1
            assert rep["lapses"] == 0
            assert rep["ret_reps_since_lapse"] == 1
            assert rep["ret_reps_since_lapse"] == 1
            assert rep["scheduled_interval"] > 60*60
            assert rep["actual_interval"] < 10
            assert rep["new_interval"] > 60*60
            assert rep["thinking_time"] < 10
            assert rep["timestamp"] > 0
    
            assert db.con.execute("select count() from log").fetchone()[0] == 13
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        fact_data = {"q": "question",
                     "a": "answer"}
        card_type = self.client.mnemosyne.card_type_by_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.review_controller().learning_ahead = True
        self.client.mnemosyne.review_controller().new_question()
        self.client.mnemosyne.review_controller().grade_answer(5)
        self.client.mnemosyne.controller().file_save()
        self.server.client_card = self.client.mnemosyne.database().\
           get_card(card.id, id_is_internal=False)        
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 13

    def test_add_media(self):

        def fill_server_database(self):
            os.mkdir(os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b"))
                     
            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b", unichr(0x628) + u"b.ogg")
            f = file(filename, "w")
            f.write("B")
            f.close()
            fact_data = {"q": "question\n<img src=\"%s\">" % (filename),
                         "a": "answer"}
            card_type = self.mnemosyne.card_type_by_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().file_save()
        
        def test_server(self):
            db = self.mnemosyne.database()
            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "a", unichr(0x628) + u"a.ogg")
            assert os.path.exists(filename)
            assert file(filename).read() == "A"
            assert db.con.execute("select count() from log").fetchone()[0] == 20
            assert db.con.execute("select count() from log where event_type=?",
                (EventTypes.ADDED_MEDIA, )).fetchone()[0] == 2      
            assert db.con.execute("""select object_id from log where event_type=?
                order by _id desc limit 1""", (EventTypes.ADDED_MEDIA, )).\
                fetchone()[0].startswith("a/")
            assert db.con.execute("select count() from media").fetchone()[0] == 2
            card = db.get_card(self.client_card.id, id_is_internal=False)
            assert card.fact["q"].startswith("question\n<img src=")
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()
        
        self.client = MyClient()

        os.mkdir(os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a"))
                     
        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a", unichr(0x628) + u"a.ogg")        
        f = file(filename, "w")
        f.write("A")
        f.close()
        fact_data = {"q": "question\n<img src=\"%s\">" % (filename),
                     "a": "answer"}
        card_type = self.client.mnemosyne.card_type_by_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().file_save()
        self.server.client_card = self.client.mnemosyne.database().\
            get_card(card.id, id_is_internal=False)  
        self.client.do_sync()

        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "b", unichr(0x628) + u"b.ogg")
        assert os.path.exists(filename)
        assert file(filename).read() == "B"
        db = self.client.mnemosyne.database()
        assert db.con.execute("select count() from log").fetchone()[0] == 20
        assert db.con.execute("select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA, )).fetchone()[0] == 2
        assert db.con.execute("select count() from media").fetchone()[0] == 2  
        assert db.con.execute("""select object_id from log where event_type=?
            order by _id desc limit 1""", (EventTypes.ADDED_MEDIA, )).\
            fetchone()[0].startswith("b/")

    def test_delete_card_with_media(self):

        def fill_server_database(self):
            os.mkdir(os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b"))
                     
            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "b", unichr(0x628) + u"b.ogg")
            f = file(filename, "w")
            f.write("B")
            f.close()
            fact_data = {"q": "question\n<img src=\"%s\">" % (filename),
                         "a": "answer"}
            card_type = self.mnemosyne.card_type_by_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.database().delete_fact_and_related_data(card.fact)
            os.remove(filename)
            self.mnemosyne.controller().file_save()
        
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
            "default.db_media", "a", unichr(0x628) + u"a.ogg")        
        f = file(filename, "w")
        f.write("A")
        f.close()
        fact_data = {"q": "question\n<img src=\"%s\">" % (filename),
                     "a": "answer"}
        card_type = self.client.mnemosyne.card_type_by_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.database().delete_fact_and_related_data(card.fact)
        os.remove(filename)
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()

    def test_update_media(self):
     
        def test_server(self):
            db = self.mnemosyne.database()
            filename = os.path.join(os.path.abspath("dot_sync_server"),
                "default.db_media", "a.ogg")
            assert os.path.exists(filename)
            assert file(filename).read() == "B"
            assert db.con.execute("""select count() from media""").fetchone()[0] == 1
            assert db.con.execute("select count() from log").fetchone()[0] == 14
            assert db.con.execute("select count() from log where event_type=?",
                (EventTypes.UPDATED_MEDIA, )).fetchone()[0] == 1

            sql_res = db.con.execute("select * from media").fetchone()
            assert sql_res["_hash"] == db._media_hash(sql_res["filename"])

        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()
            
        self.client = MyClient()

        filename = os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "a.ogg")        
        f = file(filename, "w")
        f.write("A")
        f.close()
        
        fact_data = {"q": "question <img src=\"%s\">" % (filename),
                     "a": "answer"}
        card_type = self.client.mnemosyne.card_type_by_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().file_save()

        db = self.client.mnemosyne.database()
        sql_res = db.con.execute("select * from media").fetchone()
        assert sql_res["_hash"] == db._media_hash(sql_res["filename"])

        # Sleep 1 sec to make sure the timestamp detection mechanism works.
        import time; time.sleep(1)
        
        f = file(filename, "w")
        f.write("B")
        f.close()
        
        self.client.do_sync()
        
        sql_res = db.con.execute("select * from media").fetchone()
        assert sql_res["_hash"] == db._media_hash(sql_res["filename"])
        
        assert db.con.execute("select count() from log where event_type=?",
            (EventTypes.UPDATED_MEDIA, )).fetchone()[0] == 1
        assert db.con.execute("select count() from log").fetchone()[0] == 14

    def test_mem_import(self):
            
        def fill_server_database(self):
            filename = os.path.join(os.getcwd(), "tests", "files", "1sided.mem")
            for format in self.mnemosyne.component_manager.get_all("file_format"):
                if format.__class__.__name__ == "Mnemosyne1Mem":
                    format.do_import(filename)
            self.mnemosyne.controller().file_save()
                    
        def test_server(self):
            pass
            
        self.server = MyServer()
        self.server.fill_server_database = fill_server_database
        self.server.test_server = test_server
        self.server.start()
        
        self.client = MyClient()
        self.client.do_sync()
    
        card = self.client.database.get_card("9cff728f", id_is_internal=False)
        assert card.grade == 2
        assert card.easiness == 2.5
        assert card.acq_reps == 1
        assert card.ret_reps == 0
        assert card.lapses == 0
        assert card.acq_reps_since_lapse == 1
        assert card.ret_reps_since_lapse == 0
        assert [tag.name for tag in card.tags] == ["<default>"]
        assert card.last_rep == 1247529600
        assert card.next_rep == 1247616000
        assert card.id == "9cff728f"
        
    def test_user_id_update(self):
            
        def test_server(self):
            pass
            
        self.server = MyServer()
        self.server.user_id = "new_user_id"
        self.server.test_server = test_server
        self.server.start()
        
        self.client = MyClient()
        assert self.client.mnemosyne.config()["user_id"] == "user_id"
        self.client.do_sync()
        assert self.client.mnemosyne.config()["user_id"] == "new_user_id"    

    def test_bad_password(self):

        def fill_server_database(self):
            fact_data = {"q": "question",
                         "a": "answer"}
            card_type = self.mnemosyne.card_type_by_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().file_save()
          
        def test_server(self):
            pass
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()
        
        self.client = MyClient()
        self.client.password = "wrong"
        self.client.do_sync()
        assert self.client.database.card_count() == 0

        # Server is still running now, we need to shut it down for the next
        # test.

        self.client.password = "pass"
        self.client.do_sync()
        assert self.client.database.card_count() == 1    

    def test_card_only(self):

        # Coverage only test.

        def fill_server_database(self):
            fact_data = {"q": "question",
                         "a": "answer"}
            card_type = self.mnemosyne.card_type_by_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().file_save()
          
        def test_server(self):
            pass
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()
        
        self.client = MyClient()
        self.client.capabilities = "cards"
        self.client.database.apply_log_entry = test_server # ignore errors
        self.client.do_sync()

        # Note: the sync above will not finish cleanly, as we are not prepared
        # to deal with non-fact based card data. This means that the server is
        # still running now, we need to shut it down for the next test.

        self.client.capabilities = "mnemosyne_dynamic_cards"
        self.client.do_sync()


    def test_latex(self):
        
        def fill_server_database(self):
            fact_data = {"q": "<latex>a^2</latex><$>b^2</$><$$>c^2</$$>",
                         "a": "answer"}
            card_type = self.mnemosyne.card_type_by_id("1")
            card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.mnemosyne.controller().file_save()
            assert "_media" not in card.question(exporting=True)
          
        def test_server(self):
            pass
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()
        
        self.client = MyClient()

        self.client.do_sync()
        assert os.path.exists(os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "latex",
            "28ec9eac8abe468caee402926546d10f.png"))
        assert os.path.exists(os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "latex",
            "44e557b2680adf90a549e62a6f79a50c.png"))
        assert os.path.exists(os.path.join(os.path.abspath("dot_sync_client"),
            "default.db_media", "latex",
            "ebc3d7bedc1f11e08895c3124001cbb5.png"))
        
    def test_latex_edit(self):
        
        def fill_server_database(self):
            fact_data = {"q": "<latex>a^2</latex>",
                         "a": "<latex>c^2</latex>"}
            card_type = self.mnemosyne.card_type_by_id("1")
            self.card = self.mnemosyne.controller().create_new_cards(fact_data,
               card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
            self.card.question()
            self.card.answer()
            self.mnemosyne.controller().file_save()
            new_fact_data = {"q": "<latex>b^2</latex>",
                             "a": "<latex>c^2</latex>"}            
            self.mnemosyne.controller().update_related_cards(self.card.fact,
              new_fact_data, card_type,
            new_tag_names=["default1"], correspondence=[])
            self.mnemosyne.controller().file_save()            
          
        def test_server(self):
            pass
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.fill_server_database = fill_server_database
        self.server.start()
        
        self.client = MyClient()
        self.client.do_sync()

        card = self.client.database.get_card(self.server.card.id, id_is_internal=False)
        assert len(card.tags) == 1
        assert list(card.tags)[0].name == "default1"

        assert self.client.database.con.execute("select count() from log where event_type=?",
            (EventTypes.ADDED_MEDIA, )).fetchone()[0] == 3
