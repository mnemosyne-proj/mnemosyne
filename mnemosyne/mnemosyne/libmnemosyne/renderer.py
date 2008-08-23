#
# renderer.py <Peter.Bienstman@UGent.be>
#

from component import Component


class Renderer(Component):
    
    def render_card_fields(self, card, fields):
        
        """Renders a sequence of fields from a card, e.g. by generating html 
        from them.  'fields' is typically either fact_view.q_fields or 
        fact_view.a_fields.
        
        """
        
        raise NotImplementedError
        
