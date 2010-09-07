#
# renderer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Renderer(Component):

    """Renders the contents of the Fact behind a Card to a suitable format,
    e.g. a html page, or a purely text based format.

    "used_for" = render_chain

    """

    component_type = "renderer"

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

    def render_fields(self, field_data, fields, card_type,
                      render_chain, **render_args):

        """Renders a sequence of 'fields' from the dictionary 'field_data'.
        'card_type' is passed as extra argument e.g. to determine card type
        specific formatting.
        We need to pass 'render_chain' as an argument here: a renderer can be
        used in more than one render chain, and can therefore not determine
        which render chain it is part of.

        """
        
        raise NotImplementedError



        
