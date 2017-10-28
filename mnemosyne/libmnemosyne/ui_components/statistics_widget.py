#
# statistics_widget.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_component import UiComponent


class StatisticsWidget(UiComponent):

    component_type = "statistics_widget"
    instantiate = UiComponent.LATER
    name = ""
    
    def show_statistics(self, variant):
        pass
