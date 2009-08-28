#
# configuration_widget.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.ui_component import UiComponent


class ConfigurationWidget(UiComponent):

    component_type = "configuration_widget"
    instantiate = UiComponent.LATER

    def display(self):
        pass

    def reset_to_defaults(self):
        pass

    def apply(self):
        pass
