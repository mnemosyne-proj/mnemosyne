#
# configuration_widget.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.ui_component import UiComponent


class ConfigurationWidget(UiComponent):

    component_type = "configuration_widget"
    instantiate = UiComponent.LATER

    def reset_to_defaults(self):
        pass

    def apply(self):
        pass
