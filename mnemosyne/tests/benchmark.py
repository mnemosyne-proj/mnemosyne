#!/usr/bin/env python

import os
import cProfile
import pstats

from mnemosyne.libmnemosyne import Mnemosyne

number_of_calls = 15
number_of_facts = 6000

mnemosyne = None

def startup():

    global mnemosyne

    # Note that this also includes building the queue and getting the first card.

    mnemosyne = Mnemosyne(resource_limited=True)
    mnemosyne.components = [
        ("mnemosyne.libmnemosyne.translator",
         "NoTranslation"),
        ("mnemosyne.libmnemosyne.ui_components.main_widget",
         "MainWidget"),
        ("mnemosyne.libmnemosyne.ui_components.review_widget",
         "ReviewWidget"),
        ("mnemosyne.libmnemosyne.databases.SQLite",
         "SQLite"),               
        ("mnemosyne.libmnemosyne.configuration",
         "Configuration"),          
        ("mnemosyne.libmnemosyne.loggers.sql_logger",
         "SqlLogger"),          
        ("mnemosyne.libmnemosyne.schedulers.SM2_mnemosyne",
         "SM2Mnemosyne"),
        ("mnemosyne.libmnemosyne.stopwatch",
          "Stopwatch"),
        ("mnemosyne.libmnemosyne.card_types.front_to_back",
         "FrontToBack"),
        ("mnemosyne.libmnemosyne.card_types.both_ways",
         "BothWays"),
        ("mnemosyne.libmnemosyne.card_types.three_sided",
         "ThreeSided"),
        ("mnemosyne.libmnemosyne.renderers.html_css_old",
         "HtmlCssOld"),
        ("mnemosyne.libmnemosyne.filters.escape_to_html",
         "EscapeToHtml"),
        ("mnemosyne.libmnemosyne.filters.expand_paths",
         "ExpandPaths"),
        ("mnemosyne.libmnemosyne.filters.latex",
         "Latex"),
        ("mnemosyne.libmnemosyne.controllers.default_controller",
         "DefaultController"),
        ("mnemosyne.libmnemosyne.review_controllers.SM2_controller",
         "SM2Controller"),
        ("mnemosyne.libmnemosyne.card_types.map",
         "MapPlugin"),
        ("mnemosyne.libmnemosyne.card_types.cloze",
         "ClozePlugin"),
        ("mnemosyne.libmnemosyne.plugins.cramming_plugin",
         "CrammingPlugin") ]    

    mnemosyne.initialise(basedir=os.path.abspath("dot_benchmark"))
    #mnemosyne.initialise(basedir="\SDMMC\.mnemosyne")

    mnemosyne.review_controller().reset()

    
def create_database():

    if 0:

        import time

        card_type = mnemosyne.card_type_by_id("1")
        facts = []
        from mnemosyne.libmnemosyne.fact import Fact
        for i in range(number_of_facts):    
            fact_data = {"q": "question" + str(i),
                         "a": "answer" + str(i)}
            facts.append(Fact(fact_data, card_type))

        t0 = time.time()
        for fact in facts:
            # Add fact to facts table.
            _fact_id = mnemosyne.database().con.execute("""insert into facts(id, card_type_id,
                creation_time, modification_time) values(?,?,?,?)""",
                (fact.id, fact.card_type.id, fact.creation_time,
                 fact.modification_time)).lastrowid
        print 'loop', time.time()-t0

        def fact_generator():
            for fact in facts:
                yield (fact.id, fact.card_type.id, fact.creation_time,
                 fact.modification_time)

        t0 = time.time()    
        mnemosyne.database().con.executemany("""insert into facts(id, card_type_id,
                creation_time, modification_time) values(?,?,?,?)""", fact_generator())
        print 'generator', time.time()-t0    
    
    mnemosyne.config()["upload_logs"] = False
    for i in range(number_of_facts):
        fact_data = {"q": "question" + str(i),
                     "a": "answer" + str(i)}
        if i % 2:
            card_type = mnemosyne.card_type_by_id("1")
        else:
            card_type = mnemosyne.card_type_by_id("2")            
        card = mnemosyne.controller().create_new_cards(\
            fact_data, card_type, grade=4, tag_names=["default"])[0]
        card.next_rep -= 1000*24*60*60
        mnemosyne.database().update_card(card)
    mnemosyne.database().save(mnemosyne.config()["path"])
    
def queue():
    mnemosyne.review_controller().reset()
    mnemosyne.review_controller().new_question()
    
def new_question():
    # Note that this actually also happened in startup().
    mnemosyne.review_controller().new_question()
    
def display():
    mnemosyne.review_controller().card.question()
    
def grade():
    # Note that this will also pull in a new question.
    mnemosyne.review_controller().grade_answer(0)

def grade_only():
    mnemosyne.scheduler().grade_answer(\
        mnemosyne.review_controller().card, 0)

def count_active():
    mnemosyne.scheduler().active_count()

def count_scheduled():
    mnemosyne.scheduler().scheduled_count()

def count_not_memorised():
    mnemosyne.scheduler().non_memorised_count()
    
def activate():
    mnemosyne.database().set_cards_active([(mnemosyne.card_type_by_id("1"),
        mnemosyne.card_type_by_id("1").fact_views[0])],
        [mnemosyne.database().get_or_create_tag_with_name("default1")])

def finalise():
    mnemosyne.config()["upload_logs"] = False
    mnemosyne.finalise()

def do_import():
    mnemosyne.component_manager.get_current("file_format").do_import("default.mem")

#tests = ["startup()", "create_database()", "queue()", "new_question()", "display()", "grade_only()",
#         "grade()", "count_active()", "count_scheduled()", "count_not_memorised()"]
#tests = ["startup()", "new_question()", "display()", "grade()", "activate()",
#    "finalise()"]
#tests = ["startup()", "create_database()", "new_question()", "display()",
#    "grade()", "activate()", "finalise()"]
#tests = ["startup()", "create_database()", "new_question()", "display()",
#    "grade()", "finalise()"]
tests = ["startup()", "create_database()"]

for test in tests:  
    cProfile.run(test, "mnemosyne_profile." + test.replace("()", ""))
    print
    print "*** ", test, " ***"
    print
    p = pstats.Stats('mnemosyne_profile.' + test.replace("()", ""))
    p.strip_dirs().sort_stats('cumulative').print_stats(number_of_calls)
