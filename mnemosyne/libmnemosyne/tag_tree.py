#
# tag_tree.py <Peter.Bienstman@gmail.com>
#

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component


class TagTree(Component, dict):

    """Organises the tags in a hierarchical tree. By convention, hierarchical
    levels in tags are denoted by a :: separator.

    This class is not meant to be instantiated at run time, but rather only
    when it is needed.

    The internal tree datastructure for e.g. the two tags A::B::C and A::B::D
    looks as follows:

    self["__ALL__"] = ["A"]
    self["A"] = ["A::B"]
    self["A::B"] = ["A::B::C", "A::B::D"]

    Each tree level stores the entire partial tag (i.e. A::B instead of B) to
    guarantee uniqueness.

    Apart from the dictionary in self, this class also contains
    self.display_name_for_node and self.card_count_for_node, with node being
    the index field for the main dictionary self.

    """

    def __init__(self, component_manager, count_cards=True):
        Component.__init__(self, component_manager)
        self._rebuild()
        if count_cards:
            self._recount()

    def _rebuild(self):
        for key in dict(self):
            del self[key]
        self["__ALL__"] = []
        self.display_name_for_node = {"__ALL__": _("All tags")}
        self.card_count_for_node = {}
        self.tag_for_node = {}
        # Preprocess tag names such that each tag results in a leaf of the
        # tree, i.e. if you have tags like "A::B" and "A", rename the latter
        # to "A::Untagged".
        tags = self.database().tags()
        tag_names = [tag.name for tag in tags]
        preprocessed_tag_name_for = {}
        for tag in tags:
            preprocessed_tag_name_for[tag] = tag.name
            for other_tag_name in tag_names:
                if other_tag_name.startswith(tag.name + "::") \
                    and other_tag_name != tag.name:
                    preprocessed_tag_name_for[tag] = \
                        tag.name + "::" + _("Untagged")
                    break
        # Build the actual tag tree.
        for tag in tags:
            name = preprocessed_tag_name_for[tag]
            self.tag_for_node[name] = tag
            parent = "__ALL__"
            partial_tag = ""
            for node in name.split("::"):
                if partial_tag:
                    partial_tag += "::"
                partial_tag += node
                if not partial_tag in self.display_name_for_node:
                    self[parent].append(partial_tag)
                    self[partial_tag] = []
                    self.display_name_for_node[partial_tag] = \
                        node.replace("::" + _("Untagged"), "")
                parent = partial_tag
        if "__UNTAGGED__" in self.display_name_for_node:
            self.display_name_for_node["__UNTAGGED__"] = _("Untagged")

    def _recount(self):
        for node in dict(self):
            if node == "__ALL__":
                self.card_count_for_node[node] = \
                    self.database().card_count()
            else:
                self.card_count_for_node[node] = \
                    self.database().card_count_for_tags(\
                    self.tags_in_subtree(node), active_only=False)

    def tags_in_subtree(self, node):
        tags = []
        # If an internal node is a full tag too (e.g. when you have both tags
        # 'A' and 'A::B', be sure to include the upper level too.
        if node in self.tag_for_node:
            tags.append(self.tag_for_node[node])
        # Do sublevels.
        for subnode in self[node]:
            tags.extend(self.tags_in_subtree(subnode))
        return tags

    def nodes(self):
        """Also returns internal nodes, even if they have no explicit tag
        associated with them."""
        return self.nodes_in_subtree(self["__ALL__"])

    def nodes_in_subtree(self, tree):
        nodes = []
        for node in tree:
            nodes.extend([node])
            nodes.extend(self.nodes_in_subtree(self[node]))
        return nodes

    def rename_node(self, node, new_name):
        if "," in new_name:
            self.main_widget().show_error(\
                _("Cannot rename a single tag to multiple tags."))
            return
        if new_name == "__UNTAGGED__": # Forbidden.
            new_name = "Untagged"
        for tag in self.tags_in_subtree(node):
            tag.name = tag.name.replace(node, new_name, 1)
            # Corner cases when new_name is empty.
            if tag.name == "":
                tag.name = "__UNTAGGED__"
            if tag.name.startswith("::"):
                tag.name = tag.name[2:]
            self.database().update_tag(tag)
        self.database().save()
        self._rebuild()
        self._recount()

    def delete_subtree(self, node):
        for tag in self.tags_in_subtree(node):
            self.database().delete_tag(tag)
        self.database().save()
        self._rebuild()
        self._recount()
