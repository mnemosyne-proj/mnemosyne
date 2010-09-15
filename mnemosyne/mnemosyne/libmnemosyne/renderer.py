#
# renderer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Renderer(Component):

    """Assembles a sequence of 'fields' which are keys in a dictionary 'data'
    to a certain format, e.g. a html page, or a purely text based format.
    
    Typically, 'data' is the fact data of a card, and 'fields' are the question
    and answer fields of the card's fact view.

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

    def set_property(self, property_name, property, card_type, fact_key=None):

        """Set a property (like font, colour, ..) for a certain card type.
        If fact_key is None, then this will be applied to all fact keys.

        """

        if property_name not in ["background_colour", "font", "font_colour",
                                 "alignment"]:
            raise KeyError
        if property_name == "background_colour" or \
               property_name == "alignment":
            self.config()[property_name][card_type.id] = property
            return
        self.config()[property_name].setdefault(card_type.id, {})
        for key in card_type.keys():
            self.config()[property_name][card_type.id].setdefault(key, None)
        if not fact_key:
            keys = card_type.keys()
        else:
            keys = [fact_key]
        for key in keys:
            self.config()[property_name][card_type.id][key] = property

    def render_fields(self, data, fields, card_type, **render_args):

        """Assembles a sequence of 'fields' which are keys in a dictionary
        'data'.
        
        card_type' is passed as extra argument e.g. to determine card type
        specific formatting.

        """
        
        raise NotImplementedError
