How to write a new frontend
===========================

libmnemosyne is designed in such a way that writing a new front is as painless as possible. All the code for running a GUI which is actually GUI toolkit independent is grouped in two controllers: the main ui controller and the review ui controller. In order to build a new frontend, you need to create a main widget which inherits from ``MainWidget`` and implements its interface, and similarly a review widget which inherits from ``ReviewWidget``.

In order to get a feel for how this works, it's best by starting to study the code for the ppygui_ui Windows Mobile client, which is the simplest possible frontend, as it only supports reviewing cards.

There are three files in that frontend:

* a startup script, which specifies which components your frontend wants to activate in libmnemosyne, whether you are running on a device which is resource limited, ... .

* a main widget, which corresponds to the application level widget in the GUI toolkit, and is in charge of showing error dialogs, displaying menus.

* the review widget, where you need to implement a.o. the code to display text in the question window, ... .


To give a better feeling for how the division of labour between your own new GUI code and the GUI independent code in the controllers works, consider this example from the 'add cards' functionality in the PyQt frontend.

When the user activates the menu option or icon to add cards, it will fire up a certain function, which in the PyQt frontend is called ``add_cards()``::

    QObject.connect(self.actionAddCards, SIGNAL("activated()"), MainWindow.add_cards)

The implementation of this function is rather trivial, it just calls the controller::

    def add_cards(self):
        self.controller().show_add_cards_dialog()

The code above is code you need to implement for your new frontend, but as you can see, it's rather trivial.

The controller's ``show_add_cards_dialog`` function looks like this::

    def show_add_cards_dialog(self):
        self.stopwatch().pause()
        self.component_manager.get_current("add_cards_dialog")\
            (self.component_manager).activate()
        review_controller = self.review_controller()
        review_controller.reload_counters()
        if review_controller.card is None:
            review_controller.new_question()
        else:
            review_controller.update_status_bar()
        self.stopwatch().unpause()

This is where the heavy lifting is done, but it's completely UI independent, and there should be no need for you to modify that code.

In order for the controller to know where it can find the actual add cards dialog, which for PyQt is called ``AddCardsDlg`` , you need to have that dialog derive from the abstract ``libmnemosyne.ui_components.dialogs.AddCardsDialog``, and provide an activate function, which for the PyQt toolkit is simply::

    def activate(self):
        self.exec_()

Finally, you need to register the ``AddCardsDlg`` component. That is what the following line does inside the main startup script (which for PyQt is simply called ``mnemosyne``)::

    mnemosyne.components.append(("mnemosyne.pyqt_ui.add_cards_dlg",
                                 "AddCardsDlg"))

Inside the ``AddCardsDlg``, there is of course lots of UI specific code, but once the dialog has enough data to create the cards, it simply calls::

    self.controller().create_new_cards(fact_data, card_type, grade, tag_names)

So, the ``AddCardsDlg`` should almost entirely consist of GUI dependent code. All the GUI indepedent code to actually create the cards is contained within the controller's ``create_new_cards()`` method.

If you feel like you need to override the review or the main controller provided by libmnemosyne, please let the developpers know. Either its design is not general enough, or you are trying to work against libmnemosyne rather than with it.

Tips for creating a responsive client:

* When instantiating a ``libmnemosyne.Mnemosyne`` object, there are two parameters you need to provide: ``upload_science_logs`` and ``interested_in_old_reps``. If you are writing a mobile client which syncs to a desktop version of mnemosyne, it is recommended that you don't deal with uploading the science logs yourself, but let the desktop client deal with that. As for ``interested_in_old_reps``, if your mobile client does not include graphical statistics using the revision history, it does not make sense to store this history on your device.
* The standard instantiation of a ``libmnemosyne.Mnemosyne`` object includes all components in libmnemosyne. If you are writing a mobile client with e.g. only review capabilities, it does not make sense to include all these components. See the example of the Windows Mobile ppygui_ui frontend for a client which only uses the bare minimum of components to improve startup time.
* If your mobile client does not include a card browser, you can save some disk space by not storing pregenerated questions or answers. To achieve this, make sure you do not include the regular ``SQLite`` component, but this one::

    ("mnemosyne.libmnemosyne.databases.SQLite_no_pregenerated_data",
     "SQLite_NoPregeneratedData")

* libmnemosyne does some optimisation by trying to show the next question before the grading of the previous question is completed. This improves the perceived responsiveness of the client. However, some GUI toolkits (e.g. Qt) queue widget updates and only excecute them when there is no more processing going on, thereby defeating libmnemosyne's optimisation. For that reason, there is a function ``review_widget().redraw_now`` which is used to tell the GUI toolkit to do the repaint now. If your toolkit also has similar behaviour, implementing this function can really help to mask slow database access.
* If save operations are slow on your mobile device, you might want to consider setting a larger default value instead of ``save_after_n_reps = 1`` in ``config.py``.
* If media files will never be edited outside of Mnemosyne on your mobile device, you can save time during sync by setting ``check_for_updated_media_files = False`` in ``config.py``.
* If you are really adventurous, you can set ``backup_before_sync = True`` in ``config.py``.



Notes:

* If you need access to the main widget when you are constructing the review widget, e.g. to specify it's parent, you can access it using `self.main_widget()``
* If you need access to some components of libmnemosyne to construct your widget (e.g. the configuration), these might not yet be available inside your ``__init__()`` method. In this case, you need to move that code to your widget's ``activate()`` method, at which time all the other compoments will already be active.
* Everything described here applies not only for Python frontends, but also for frontends not written in Python, which access libmnemosyne through an UDP socket or through the Python-embedded-in-C bridge.
