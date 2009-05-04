#!/usr/bin/env python

import os
import cProfile
import pstats

from mnemosyne.libmnemosyne import Mnemosyne
from mnemosyne.libmnemosyne.component_manager import database, config
from mnemosyne.libmnemosyne.component_manager import card_type_by_id
from mnemosyne.libmnemosyne.component_manager import ui_controller_main
from mnemosyne.libmnemosyne.component_manager import ui_controller_review

number_of_calls = 15
number_of_facts = 6000

def init():
    mnemosyne = Mnemosyne(resource_limited=True)
    mnemosyne.initialise(basedir=os.path.abspath("dot_benchmark"), main_widget=None,
                         extra_components=[("HtmlCssOld",
                        "mnemosyne.libmnemosyne.renderers.html_css_old")])

def create_database():
    config()["upload_logs"] = False

    for i in range(number_of_facts):
        fact_data = {"q": "question" + str(i),
                     "a": "answer" + str(1)}
        if i % 2:
            card_type = card_type_by_id("1")
        else:
            card_type = card_type_by_id("2")            
        card = ui_controller_main().create_new_cards(fact_data, card_type,
                           grade=4, cat_names=["default" + str(i)])[0]
        card.next_rep -= 1000
        database().update_card(card)
    database().save(config()["path"])
    
def question():
    ui_controller_review().new_question()
    
def display():
    ui_controller_review().card.question()
    
def grade():
    ui_controller_review().grade_answer(0)

def activate():
    database().set_cards_active([(card_type_by_id("1"),
                                 card_type_by_id("1").fact_views[0])],
        [database().get_or_create_category_with_name("default1")])

def finalise():
    config()["upload_logs"] = False
    Mnemosyne().finalise()

tests = ["init()", "question()", "display()", "grade()"]
tests = ["init()", "question()", "display()", "grade()", "activate()", "finalise()"]
tests = ["init()", "create_database()", "question()", "display()", "grade()",
         "activate()", "finalise()"]
tests = ["init()"]

for test in tests:  
    cProfile.run(test, "mnemosyne_profile")
    print
    print "*** ", test, " ***"
    print
    p = pstats.Stats('mnemosyne_profile')
    p.strip_dirs().sort_stats('cumulative').print_stats(number_of_calls)
