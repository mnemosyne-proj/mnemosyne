How to write a new frontend
===========================

libmnemosyne is designed in such a way that writing a new front is as painless as possible. All the code for running a GUI which is actually GUI toolkit independent is grouped in two controllers: the main ui controller and the review ui controller. In order to build a new frontend, you need to create a main widget which inherits from ``MainWidget`` and implements its interface, and similarly a review widget which inherits from ``ReviewWidget``.

In order to get a feel for how this works, it's best by starting to study the code for the ppygui_ui Windows Mobile client, which is the simplest possible frontend, a it only supports reviewing cards.

There a three files in that frontend:

* a startup script, which specifies which compoments your frontend wants to activate in libmnemosyne, whether you are running on a device which is resource limited, ... .

* the review widget, where you need to implement a.o. the code to display text in the question window, ... .

* a main window, which in the windows mobile backend is just a container for the review widget, but which in a more advanced client could contain the functionality needed to add cards, edit cards, etc...

To give a better feeling for how the division of labour between your own new GUI code and the GUI independent code in the controllers works, consider this example from the 'add cards' functionality in the PyQt frontend.

When the user activates the menu option or icon to add cards, it will fire up a certain function, which in the PyQt frontend is called ``add_cards()``::

    QObject.connect(self.actionAddCards, SIGNAL("activated()"), MainWindow.add_cards)

The implementation of this function is rather trivial, it just calls the ui controller::

    def add_cards(self):
        self.ui_controller_main().add_cards()

The code above is code you need to implement for your new frontend, but as you can see, it's rather trivial.

The ui_controller_main add cards function looks like this::

    def add_cards(self):
        stopwatch.pause()
        self.main_widget().run_add_cards_dialog()
        review_controller = self.ui_controller_review()
        review_controller.reload_counters()
        if review_controller.card == None:
            review_controller.new_question()
        else:
            self.review_widget().update_status_bar()
        stopwatch.unpause()

This is where the heavy lifting is done, but it's completely UI independent, 
and there should be no need for you to modify that code.

To enable the controller to do it's actual work, you need to write the 
callback ``main_widget().run_add_cards_dialog()``, but as you can see, the code 
you need to write yourself is again rather trivial::
        
    def run_add_cards_dialog(self):
        dlg = AddCardsDlg(self, self.component_manager)
        dlg.exec_()

Inside the ``AddCardsDlg``, there is of course lots of UI specific code, but once 
the dialog has enough data to create the cards, it simply calls::

    self.ui_controller_main().create_new_cards(fact_data, card_type, grade, cat_names)

So, the ``AddCardsDlg`` should almost entirely consist of GUI dependent code. All the GUI indepedent code to actually create the cards is contained within the ui controller's ``create_new_cards()`` method.

If you feel like you need to override the review or the main ui controller provided by libmnemosyne, please let the developpers know. Either its design is not general enough, or you are trying to work against libmnemosyne rather than with it.

Notes:

* If you need access to the main widget when you are constructing the review widget, e.g. to specify it's parent, you can access it using `self.main_widget()``
* If you need access to some components of libmnemosyne to construct your widget (e.g. the configuration), these might not yet be available inside your ``__init__()`` method. In this case, you need to move that code to your widget's ``activate()`` method, at which time all the other compoments will already be active.