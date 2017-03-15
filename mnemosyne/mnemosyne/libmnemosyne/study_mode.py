#
# study_mode.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class StudyMode(Component):
    
    """A study mode is a collection of a scheduler and a review controller. 
    Different study modes can share e.g. the same scheduler, but instantiated
    with different parameters."""

    id = 0  # To determine sorting order in menu
    name = ""  # Menu text
    component_type = "study_mode"
    Scheduler = None  # Class
    ReviewController = None  # Class

    def register_components(self):
        # Scheduler.
        previous_scheduler = self.scheduler()
        if previous_scheduler:
            previous_scheduler.deactivate()
            self.component_manager.unregister(previous_scheduler)
        self.component_manager.register(\
            self.Scheduler(self.component_manager))
        self.log().started_scheduler()
        self.log().loaded_database()  # Backwards compatibility
        self.log().future_schedule()
        # Review controller.
        previous_review_controller = self.review_controller()
        if previous_review_controller:
            previous_review_controller.deactivate()
            self.component_manager.unregister(previous_review_controller)
        self.component_manager.register(\
            self.ReviewController(self.component_manager)) 
                
    def activate(self):
        self.register_components()
        self.review_controller().reset()
        
