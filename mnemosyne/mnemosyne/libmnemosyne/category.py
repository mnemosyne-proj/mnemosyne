
##############################################################################
#
# category.py <Peter.Bienstman@UGent.be>
#
##############################################################################



##############################################################################
#
# Category
#
##############################################################################

categories = []
category_by_name = {}

class Category:
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, name, active=True):

        self.name = name
        self.active = active

    ##########################################################################
    #
    # in_use
    #
    ##########################################################################

    def in_use(self):

        used = False

        for e in cards:
            if self.name == e.cat.name:
                used = True
                break

        return used



##############################################################################
#
# get_categories
#
##############################################################################

def get_categories():
    return categories



##############################################################################
#
# get_category_names
#
##############################################################################

def get_category_names():
    return sorted(category_by_name.keys())



##############################################################################
#
# ensure_category_exists
#
##############################################################################

def ensure_category_exists(name):

    global category_by_name, categories

    if name not in category_by_name.keys():
        category = Category(name)
        categories.append(category)
        category_by_name[name] = category



##############################################################################
#
# get_category_by_name
#
##############################################################################

def get_category_by_name(name):

    global category_by_name

    ensure_category_exists(name)
    return category_by_name[name]



##############################################################################
#
# remove_category_if_unused
#
##############################################################################

def remove_category_if_unused(cat):

    global cards, category_by_name, categories

    for card in cards:
        if cat.name == card.cat.name:
            break
    else:
        del category_by_name[cat.name]
        categories.remove(cat)
