#
# tag.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.utils import rand_uuid, CompareOnId


class Tag(CompareOnId):
    
    """The tag name is the full name, including all levels of the hierarchy
    separated by two colons.

    'id' is used to identify this object to the external world (logs, xml
    files, ...), whereas '_id' is an internal id that could be different and
    that can be used by the database for efficiency reasons.

    Untagged cards are given the internal tag __UNTAGGED__, to allow for a
    fast implementation of applying activity criteria.
    
    """

    def __init__(self, name, id=None):
        if id is None:
            id = rand_uuid()
        self.id = id
        self._id = None
        self.name = name
        self.extra_data = {}


from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import numeric_string_cmp

class TagsTree(Component):
    

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)


        # A::B::C and A::B::D
        # Each tree level stores the entire partial tag (i.e. A::B instead
        # of B) to guarantee uniqueness.

        # Internal nodes have an id ending on ::, leaves don't end on
        #self.tree[_("__ALL__")] = ["A::"]
        #self.tree["A::"] = ["A::B::"]
        #self.tree["A::B::"] = ["A::B::C", "A::B::D"]

        self.tree = {"__ALL__": []}
        self.display_name_for_node = {"__ALL__": _("All tags")}
        self.card_count_for_node = {"__ALL__": -1}  # To be determined later.
        tag_names = sorted([tag.name for tag in self.database().tags()],
            cmp=numeric_string_cmp)
        for tag_name in tag_names:
            if tag_name == "__UNTAGGED__":
                continue  # Add it at the very end for esthetical reasons.
            parent = "__ALL__"
            partial_tag = ""
            levels = tag_name.split("::")
            # Branches.
            for node in levels[:-1]:
                node += "::"
                partial_tag += node
                if not partial_tag in self.display_name_for_node:
                    self.tree[parent].append(partial_tag)
                    self.display_name_for_node[partial_tag] = node[:-2]
                    self.card_count_for_node[partial_tag] = -1  # For later. 
                parent = partial_tag
            # Leaf.
            self.tree[parent].append(tag_name)
            self.display_name_for_node[tag_name] = levels[-1]
            self.card_count_for_node[tag_name] = \
                self.database().total_card_count_for_tag\
                (self.database().get_or_create_tag_with_name(tag_name))
        if "__UNTAGGED__" in tag_names:
            self.tree["__ALL__"].append("__UNTAGGED__")
            self.display_name_for_node["__UNTAGGED__"] = _("Untagged")
        # Determine card count in interval nodes.

        # Todo
        
        print self.tree

        
