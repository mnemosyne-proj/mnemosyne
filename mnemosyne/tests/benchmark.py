#!/usr/bin/env python

import os
import time
import pstats
import cProfile

from mnemosyne.libmnemosyne import Mnemosyne

number_of_calls = 15 # Number of calls to display in profile
number_of_facts = 6000

mnemosyne = None

def startup():

    global mnemosyne

    # Note that this also includes building the queue and getting the first card.

    mnemosyne = Mnemosyne(upload_science_logs=False)
    mnemosyne.components.insert(0,
        ("mnemosyne.libmnemosyne.translator",
         "NoTranslation"))
    mnemosyne.components.append(    
        ("mnemosyne.libmnemosyne.ui_components.main_widget",
         "MainWidget"))
    mnemosyne.components.append(
        ("mnemosyne.libmnemosyne.ui_components.review_widget",
         "ReviewWidget"))

    mnemosyne.initialise(data_dir=os.path.abspath("dot_benchmark"),
        automatic_upgrades=False)
    #mnemosyne.initialise(data_dir="\SDMMC\.mnemosyne",
    #automatic_upgrades=False)

    mnemosyne.review_controller().reset()

def create_database():
    mnemosyne.database().new(mnemosyne.config()["path"])
    for i in range(number_of_facts):
        fact_data = {"q": "question" + str(i),
                     "a": "answer" + str(i)}
        if i % 2:
            card_type = mnemosyne.card_type_by_id("1")
        else:
            card_type = mnemosyne.card_type_by_id("2")
        card = mnemosyne.controller().create_new_cards(\
            fact_data, card_type, grade=4, tag_names=["default"],
            check_for_duplicates=False, save=False)[0]
        card.next_rep = time.time() - 24 * 60 * 60
        card.last_rep = card.next_rep - i * 24 * 60 * 60
        mnemosyne.database().update_card(card)
    mnemosyne.database().save()

def queue():
    mnemosyne.review_controller().reset()

def new_question():
    # Note that this actually also happened in startup().
    mnemosyne.review_controller().new_question()

def display():
    mnemosyne.review_controller().card.question()

def grade():
    # Note that this will also pull in a new question.
    mnemosyne.review_controller().grade_answer(0)
    
def grade_2():
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
    from mnemosyne.libmnemosyne.activity_criteria.default_criterion import \
     DefaultCriterion
    card_type_2 = mnemosyne.card_type_by_id("2")
    c = DefaultCriterion(mnemosyne.component_manager)
    c.active_tags__ids = set([mnemosyne.database().get_or_create_tag_with_name("default")._id])
    c.forbidden_tag__ids = set()
    c.deactivated_card_type_fact_view_ids = \
        set([(card_type_2.id, card_type_2.fact_views[0].id)])
    c.active_tag__ids = set([mnemosyne.database().get_or_create_tag_with_name("default")._id])
    c.forbidden_tags__ids = set()
    mnemosyne.database().set_current_activity_criterion(c)

def finalise():
    mnemosyne.finalise()

def do_import():
    mnemosyne.component_manager.current("file_format").\
        do_import("/home/pbienst/dot_mnemosyne/default.mem")

tests = ["startup()", "create_database()", "queue()", "new_question()", "display()", "grade_only()",
         "grade()", "grade_2()", "count_active()", "count_scheduled()", "count_not_memorised()"]
tests = ["startup()", "new_question()", "display()", "grade()", "grade_2()", "activate()",
    "finalise()"]
#tests = ["startup()", "create_database()", "new_question()", "display()",
#    "grade()", "activate()", "finalise()"]
#tests = ["startup()", "create_database()", "new_question()", "display()",
#    "grade()", "finalise()"]
#tests = ["startup()", "create_database()", "activate()"]
#tests = ["startup()", "do_import()", "finalise()"]
#tests = ["startup()", "queue()", "finalise()"]
#tests = ["startup()", "activate()"]
tests = ["startup()", "finalise()"]

for test in tests:
    cProfile.run(test, "mnemosyne_profile." + test.replace("()", ""))
    print
    print "*** ", test, " ***"
    print
    p = pstats.Stats('mnemosyne_profile.' + test.replace("()", ""))
    p.strip_dirs().sort_stats('cumulative').print_stats(number_of_calls)

# 5.2 0.92
