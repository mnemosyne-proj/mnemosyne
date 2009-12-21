#
# test_sync.py <Peter.Bienstman@UGent.be>
#

import os
from threading import Thread
from openSM2sync.server import Server
from openSM2sync.client import Client
from openSM2sync.log_entry import EventTypes

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.fact import Fact
from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget

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
    capabilities = "TODO"

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
     
    def authorise(self, login, password):
        return login == "user" and password == "pass"

    def open_database(self, database_name):
        self.database = self.mnemosyne.database()

    def run(self):
        # We only open the database connection inside the thread to prevent
        # access problems, as a single connection can only be used inside a
        # single thread.
        self.mnemosyne.initialise(os.path.abspath(os.path.join(os.getcwdu(),
                                  "dot_sync_server")))
        self.fill_server_database()
        Server.__init__(self, "127.0.0.1", 8014, self.mnemosyne.main_widget())
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
        
    def fill_server_database(self):
        pass

    def test(self):
        raise NotImplementedError


class MyClient(Client):
    
    program_name = "Mnemosyne"
    program_version = "test"
    capabilities = "TODO"
    
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
        self.mnemosyne.review_controller().reset()        
        Client.__init__(self, self.mnemosyne.database(),
                        self.mnemosyne.main_widget())
        
    def do_sync(self):
        self.sync("http://127.0.0.1:8014", "user", "pass")


class TestSync(object):

    def teardown(self):
        self.client.mnemosyne.finalise()
        assert self.server.passed_tests == True
        
    def test_add_tag(self):

        def test_server(self):
            db = self.mnemosyne.database()
            tag = db.get_or_create_tag_with_name(unichr(40960) + u'>&<abcd')
            assert tag.id == self.client_tag_id
            assert tag.name == unichr(40960) + u">&<abcd"
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
              get_or_create_tag_with_name(unichr(40960) + u">&<abcd")
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
            assert fact.data == {"q": "Q", "a": "A"}
            assert fact.card_type == self.mnemosyne.card_type_by_id("1")
            assert fact.creation_time == self.client_creation_time
            assert fact.modification_time == self.client_creation_time
            assert db.con.execute("select count() from log").fetchone()[0] == 8 
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()

        self.client = MyClient()
        card_type = self.client.mnemosyne.card_type_by_id("1")
        fact = Fact({"q": "Q", "a": "A"}, card_type)
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
            assert db.con.execute("select count() from log").fetchone()[0] == 10
            
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
        self.client.do_sync()
        assert self.client.mnemosyne.database().con.execute(\
            "select count() from log").fetchone()[0] == 10
        
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
    
            assert db.con.execute("select count() from log").fetchone()[0] == 14
            
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
            "select count() from log").fetchone()[0] == 14

    def test_add_media(self):
        
        def test_server(self):
            db = self.mnemosyne.database()
            
        self.server = MyServer()
        self.server.test_server = test_server
        self.server.start()
        
        self.client = MyClient()
        file("a.ogg", "w")
        filename = os.path.abspath("a.ogg")
        fact_data = {"q": "question <img src=\"%s\">" % (filename),
                     "a": "answer"}
        card_type = self.client.mnemosyne.card_type_by_id("1")
        card = self.client.mnemosyne.controller().create_new_cards(fact_data,
            card_type, grade=4, tag_names=["tag_1", "tag_2"])[0]
        self.client.mnemosyne.controller().file_save()
        self.client.do_sync()
