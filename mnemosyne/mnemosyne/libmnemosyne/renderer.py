#
# renderer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Renderer(Component):

    """Renders the contents of the Fact behind a Card to a suitable format,
    e.g. a html page, or a purely text based format.

    The 'used_for' argument contains a string to signal the render chain
    in which the rendere is used ('default', 'plain_text', ...)

    If this renderer is only for a specific card type (and it's descendants)
    'card_type' can be set to the corresponding CardType class. If 'card_type' 
    is None, this renderer is used for all other card types.

    """

    component_type = "renderer"
    used_for = ""
    card_type = None # Used for all card types.

    def update(self, card_type):

        """Update renderer information for given card type."""
        
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

    def render_fields(self, field_data, fields, card_type, **render_args):

        """Renders a sequence of 'fields' from the dictionary 'field_data'.
        'card_type' is passed as extra argument e.g. to determine card type
        specific formatting.

        """
        
        raise NotImplementedError
    
