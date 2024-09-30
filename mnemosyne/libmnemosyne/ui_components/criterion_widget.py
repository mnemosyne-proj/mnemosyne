#
# criterion_widget.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.ui_component import UiComponent


class CriterionWidget(UiComponent):

    component_type = "criterion_widget"
    instantiate = UiComponent.LATER      

    def display_criterion(self, criterion):
        raise NotImplementedError

    def criterion(self):
        raise NotImplementedError