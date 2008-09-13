.. libmnemosyne documentation master file, created by sphinx-quickstart on Sat Aug  9 10:59:10 2008.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Libmnemosyne overview
==============================

Libmnemosyne consists of a number of Components, which can be swapped in and
out. This is handled by the ComponentManager. Examples of Components are the
scheduler, the storage layer, card types, plugins, ...

The basic unit of information from which Cards are derived is called a Fact,
containing a set of fields and their associated values. E.g., for a three-sided 
CardType, these fields are foreign word, pronunciation and translation.

A FactView collects a number of the fields of a Fact into question and answers.
E.g., the three-sided CardType has a recognition FactView, where the question
contains the foreign word, and the answer contains the pronunciation and the 
translation.

As mentioned before, a Fact is linked to a CardType, and each CardType lists
a set of FactViews.

The actual Cards are generated from the data in Fact using the recipe of a
certain FactView. A Card also contains all the revision data needed for the
Scheduler to do its work. Since the question and answers are generated from
the Fact data each time a Card is shown, related Cards (i.e. Cards with
different FactViews of the same Fact) are always consistent.

The actual displaying of the data in a Card is handled by a Renderer. The 
default Renderer takes the fields from the Fact, adds them into a html template
and applies a CSS for formatting.

In order to make it easier for other GUI frontends to be written, all the logic
typically needed for GUIs, but that is independent of the actual GUI toolkit
used, is abstracted in ui controllers. In order to get more flexibility, there 
are two of them: one related to the review widget, and one to the rest 
of the program.

Modules
=======

.. toctree::
    :maxdepth: 2
    
    modules/component
    modules/component_manager
    modules/fact
    modules/fact_view
    modules/card_type
    modules/card  
    modules/renderer
    modules/ui_controller_main
    modules/ui_controller_review
    modules/review_widget
    modules/category
    modules/configuration
    modules/database
    modules/file_format
    modules/filter
    modules/function_hook
    modules/log_uploader
    modules/logger
    modules/plugin
    modules/scheduler
    modules/stopwatch
    
     
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


