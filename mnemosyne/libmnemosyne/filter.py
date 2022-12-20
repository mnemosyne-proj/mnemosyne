#
# filter.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component


class Filter(Component):

    """Code which operates on a string and filters it to achieve extra
    functionality, e.g. converting relative paths to absolute paths.

    It is contained in a RenderChain and represents functionality which is
    useful for many different card types.

    The filters are executed in the order they are listed in the RenderChain.
    If you really need to make sure that your filter runs before the
    rest, set 'in_front=True' as argument in 'render_chain.register_filter'.
    
    """

    component_type = "filter"

    def run(self, text, card, fact_key, **render_args):
        raise NotImplementedError
