#
# renderer.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Renderer(Component):

    """Renders the contents of the Fact behind a Card to a suitable format.

    "used_for" = card_type class

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
        print "Setting property", property_name, self.config()[property_name]

        
    def render_card_fields(self, card, fields):
        
        """Renders a sequence of fields from a card, e.g. by generating html 
        for them.  'fields' is typically either fact_view.q_fields or 
        fact_view.a_fields.
        
        """
        
        raise NotImplementedError

    def render_text(self, text, field_name, card_type):

        """A lower lever renderer, rendering 'text' from a field with name
        'field_name' from 'card_type'.

        """

        raise NotImplementedError


        
