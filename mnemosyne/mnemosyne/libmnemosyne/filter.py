#
# filter.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Filter(Component):

    """Code which operates on a string and filters it to achieve extra 
    functionality, e.g. converting relative paths to absolute paths.

    The filter is 'used_for' one or more render chains.

    The filters are executed in the order they are listed in the component
    manager. If you really need to make sure that your filter runs before the
    rest, set 'in_front=True' as argument in 'component_manager.register'.
    
    """

    component_type = "filter"
    used_for = "default"

    def run(self, text, **render_args):
        raise NotImplementedError
