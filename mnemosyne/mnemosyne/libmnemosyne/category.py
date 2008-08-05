
##############################################################################
#
# category.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from mnemosyne.libmnemosyne.component_manager import get_database




##############################################################################
#
# Category
#
#  The category name is the full name, including all levels of the hierarchy
#  separated by ::
#
##############################################################################

class Category:
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, name):

        self.name = name


    
    ##########################################################################
    #
    # in_use
    #
    #  TODO: move to database
    #
    ##########################################################################

    def in_use(self):

        used = False

        for c in get_database.get_cards():
            if self.name == c.cat.name:
                used = True
                break

        return used




# TODO: see if still needed.

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
        

