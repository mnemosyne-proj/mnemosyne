
##############################################################################
#
# category.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from mnemosyne.libmnemosyne.plugin_manager import get_database




##############################################################################
#
# Category
#
##############################################################################

categories = []


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
    # save
    #
    ##########################################################################

    def save(name):

        get_database.add_category(self)


    
    ##########################################################################
    #
    # in_use
    #
    #  TODO: better to move to database?
    #
    ##########################################################################

    def in_use(self):

        used = False

        for c in get_database.get_cards():
            if self.name == c.cat.name:
                used = True
                break

        return used




# TODO: see if needed anymore

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


