##############################################################################
#
# ui_controller.py <Peter.Bienstman@UGent.be>
#
##############################################################################

ui_controller = []



##############################################################################
#
# UiController
#
##############################################################################

class UiController(object):

    def __init__(self, widget, scheduler):

        self.widget = widget
        sef.scheduler = scheduler

    def new_question(self):
        raise NotImplementedError()



    # TODO: list calls make back to widget


    
##############################################################################
#
# register_ui_controller
#
#  Note: 'ui_controller' is a list, the idea being that if the user
#  unregisters a custom ui_controller, there is still the default
#  ui_controller which we can access.
#
##############################################################################

def register_ui_controller(ui_controller_class, widget):

    global ui_controller

    ui_controller.append(ui_controller_class(widget))



##############################################################################
#
# unregister_ui_controller
#
##############################################################################

# TODO: test

def unregister_ui_controller(ui_controller_class):

    global ui_controller

    for s in ui_controller:
        if isinstance(s. ui_controller_class):
            s.widget.close()
            schedule.remove(s)
            break



##############################################################################
#
# get_ui_controller
#
##############################################################################

def get_ui_controller():

    return ui_controller[-1]
