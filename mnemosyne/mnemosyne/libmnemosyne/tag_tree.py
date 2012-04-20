#
# tag_tree.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component


class TagTree(Component, dict):

    """Organises the tags in a hierarchical tree. By convention, hierarchical
    levels in tags are denoted by a :: separator.

    This class is not meant to be instantiated at run time, but rather only
    when it is needed.

    The internal tree datastructure for e.g. the two tags A::B::C and A::B::D
    looks as follows:

    self[_("__ALL__")] = ["A"]
    self["A"] = ["A::B"]
    self["A::B"] = ["A::B::C", "A::B::D"]

    Each tree level stores the entire partial tag (i.e. A::B instead of B) to
    guarantee uniqueness.

    Apart from the dictionary in self, this class also contains
    self.display_name_for_node and self.card_count_for_node, with node being
    the index field for the main dictionary self.

    """

    def __init__(self, component_manager):
        Component.__init__(self, component_manager)
        self._rebuild()

    def _rebuild(self):
        for key in dict(self):
            del self[key]
        self["__ALL__"] = []
        self.display_name_for_node = {"__ALL__": _("All tags")}
        self.card_count_for_node = {}
        self.tag_for_node = {}
        for tag in self.database().tags():
            self.tag_for_node[tag.name] = tag
            parent = "__ALL__"
            partial_tag = ""
            for node in tag.name.split("::"):
                if partial_tag:
                    partial_tag += "::"
                partial_tag += node
                if not partial_tag in self.display_name_for_node:
                    self[parent].append(partial_tag)
                    self[partial_tag] = []
                    self.display_name_for_node[partial_tag] = node
                parent = partial_tag
        if "__UNTAGGED__" in self.display_name_for_node:
            self.display_name_for_node["__UNTAGGED__"] = _("Untagged")
        for node in dict(self):
            self.card_count_for_node[node] = \
                self.database().card_count_for_tags(\
                self._tags_in_subtree(node), active_only=False)

    def _tags_in_subtree(self, node):
        tags = []
        # If an internal node is a full tag too (e.g. when you have both tags
        # 'A' and 'A::B', be sure to include the upper level too.
        if node in self.tag_for_node:
            tags.append(self.tag_for_node[node])
        # Do sublevels.
        for subnode in self[node]:
            tags.extend(self._tags_in_subtree(subnode))
        return tags

    def rename_node(self, old_node_label, new_node_label):
        if new_node_label == "__UNTAGGED__": # Forbidden.
            new_node_label = "Untagged"
        for tag in self._tags_in_subtree(old_node_label):
            tag.name = tag.name.replace(old_node_label, new_node_label, 1)
            # Corner cases when new_node_label is empty.
            if tag.name == "":
                tag.name = "__UNTAGGED__"
            if tag.name.startswith("::"):
                tag.name = tag.name[2:]
            self.database().update_tag(tag)
        self.database().save()
        self._rebuild()

    def delete_subtree(self, node):
        for tag in self._tags_in_subtree(node):
            self.database().delete_tag(tag)
        self.database().save()
        self._rebuild()
