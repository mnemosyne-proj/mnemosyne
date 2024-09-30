#
# renderer.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.component import Component


class Renderer(Component):

    """Assembles a sequence of 'fact_keys' which are keys in a dictionary
    'fact_data' to a certain format, e.g. a html page, or a purely text based
    format.
    
    Typically 'fact_keys' are the question and answer keys of the card's fact
    view.

    It is contained in a RenderChain and represents the functionality which
    is typically different for each card type.

    If this renderer is only for a specific card type (and its descendants)
    'used_for' can be set to the corresponding CardType class. If it is set to
    None, this renderer is used for all other card types.

    """

    component_type = "renderer"
    used_for = None  # Used for all card types.

    def update(self, card_type):

        """Update renderer information for given card type. Some information
        (e.g. css style sheets) is typically cached, and this function is
        used to signal that the cache should be rebuilt.

        """
        
        pass

    def render(self, fact_data, fact_keys, card_type, **render_args):

        """Assembles a sequence of 'fact_keys' which are keys in a dictionary
        'fact_data'.
        
        card_type' is passed as extra argument e.g. to determine card type
        specific formatting.

        """
        
        raise NotImplementedError
