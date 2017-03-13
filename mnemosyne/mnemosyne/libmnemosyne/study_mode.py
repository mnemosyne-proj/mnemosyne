#
# study_mode.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class StudyMode(Component):
    
    """A study mode is a collection of a scheduler, review controller and
    (optionally) a review widget. 
    
    Different study modes can share e.g. the same scheduler, but instantiated
    with different parameters."""

    id = 0  # To determine sorting order in menu
    name = ""  # Menu text
    component_type = "study_mode"

    def activate(self):
        raise NotImplementedError
