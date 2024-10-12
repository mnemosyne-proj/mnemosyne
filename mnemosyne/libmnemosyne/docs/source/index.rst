.. libmnemosyne documentation master file, created by sphinx-quickstart on Sat Aug  9 10:59:10 2008.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Libmnemosyne overview
==============================

Libmnemosyne consists of a number of components, which can be swapped in and
out. This is handled by the ComponentManager. Examples of components are the
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
certain FactView. A Card also contains all the repetition data needed for the
Scheduler to do its work. Since the question and answers are generated from
the Fact data each time a Card is shown, related Cards (i.e. Cards with
different FactViews of the same Fact) are always consistent.

The actual displaying of the data in a Card is handled by a RenderChain, which
details the operations needed to get from the raw data in a Card to a
representation of its question and answer, in a form either suitable for
displaying in a browser, or exporting to a text file, ... . First the raw data
is sent through Filters, which perform operations which can be useful for many
card types, like expanding relative paths. Then this data is assembled in the
right order in a Renderer, which can be card type specific.

At several points in the program, plugin writers can hook in their code using
the Hook mechanism.

Before the data is passed to the Renderer, Filters can be applied to it. This
is an extra level of flexibility, and can be used to generate LaTeX, convert
relative paths to absolute paths, etc ...

To determine which cards are active (i.e.) participate in the review process,
a mechanism of ActivityCriterion and CriterionApplier is used.

In order to make it easier for other GUI frontends to be written, all the logic
typically needed for GUIs, but that is independent of the actual GUI toolkit
used, is abstracted in controllers. In order to get more flexibility, there
are two of them: one related to the review process (which is different for
different schedulers), and one related to the rest of the program (which
normally won't change).

There is also mechanism for plugins to add new statistical data to the standard
statistics in an integrated way.


Contents
========

.. toctree::
    :maxdepth: 2

    modules/component
    modules/component_manager
    modules/fact
    modules/fact_view
    modules/tag
    modules/tag_tree
    modules/card_type
    modules/card
    modules/card_type_converter
    modules/render_chain
    modules/filter
    modules/renderer
    modules/controller
    modules/review_controller
    modules/study_mode
    modules/configuration
    modules/database
    modules/file_format
    modules/hook
    modules/log_uploader
    modules/logger
    modules/plugin
    modules/scheduler
    modules/stopwatch
    modules/statistics_page
    modules/criterion
    modules/language
    modules/translator
    modules/pronouncer

    modules/how_to_write_a_new_frontend


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
