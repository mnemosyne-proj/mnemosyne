##############################################################################
#
# file_format.py <Peter.Bienstman@UGent.be>
#
##############################################################################

from mnemosyne.libmnemosyne.component import Component



##############################################################################
#
# FileFormat
#
##############################################################################

class FileFormat(Component):

    ##########################################################################
    #
    # __init__
    #
    # The filename filter has to be given in Qt format, e. g.
    #  XML Files (*.xml *XML)".
    #
    ##########################################################################

    def __init__(self, name, description, filename_filter):

        self.name            = name
        self.description     = description
        self.filename_filter = filename_filter
        self.import_possible = import_possible
        self.export_possible = export_possible



    ##########################################################################
    #
    # Functions to be implemented by the actual file format.
    #
    ##########################################################################

    def do_import(self, filename, default_cat_name,
                  reset_learning_data=False):
        raise NotImplementedError

    def do_export(self, filename, default_cat_name,
                  reset_learning_data=False):
        raise NotImplementedError    




# TODO: integrate code below


##############################################################################
#
# anonymise_id
#
#   Returns anonymous version of id (_0, _1, ...), but keeps card's
#   original id intact.
#
# TODO: probably not needed anymore
#
##############################################################################

id_to_anon = {}

def anonymise_id(card):
    
    global id_to_anon

    if '.' in card.id:
        old_id, suffix = card.id.split('.', 1)
    else:
        old_id, suffix = card.id, ''

    if suffix:
        suffix = '.' + suffix
    
    return id_to_anon.setdefault(old_id, '_'+str(len(id_to_anon)))+suffix



##############################################################################
#
# unanonymise_id
#
#   Create a new id from an anonymous one, and updates card's id with it.
#
# TODO: probably only needed when importing 1.x XML
#
##############################################################################

anon_to_id = {}

def unanonymise_id(card):
    global anon_to_id
    if '.' in card.id:
        old_id, suffix = card.id.split('.', 1)
    else:
        old_id, suffix = card.id, ''
    if suffix:
        suffix = '.' + suffix
    if old_id.startswith('_'):
        if old_id in anon_to_id:
            card.id = anon_to_id[old_id] + suffix
        else:
            card.new_id()
            anon_to_id[old_id] = card.id
            card.id += suffix
    return card.id



##############################################################################
#
# import_file
#
##############################################################################

def import_file(filename, fformat_name, default_cat_name,
                reset_learning_data=False):

    global load_failed, revision_queue, anon_to_id

    # If no database is active, create one.

    if not time_of_start:
        new_database(config["path"])

    # Call import function according to file format name.

    default_cat = get_category_by_name(default_cat_name)
    fformat = get_file_format_from_name(fformat_name)
    imported_cards = fformat.import_function(filename, default_cat,
                                             reset_learning_data)

    # Add new cards.
    
    for card in imported_cards:
        # Check for duplicates.
        for i in get_cards():
            if i.q == card.q and i.a == card.a:
                if get_config("check_duplicates_when_adding") == True:
                    if get_config("allow_duplicates_in_diff_cat") == False:
                        break
                    elif i.cat == card.cat:
                        break
        else:
            cards.append(card)
            if card.is_due_for_retention_rep():
                revision_queue[0:0] = [card]
            log().imported_card(card) 
    # Clean up.

    remove_category_if_unused(default_cat)

    load_failed = False

    anon_to_id = {}



##############################################################################
#
# export_file
#
##############################################################################

def export_file(filename, fformat_name,
                cat_names_to_export, reset_learning_data):

    global id_to_anon
    
    # Call export function according to file format name.

    fformat = get_file_format_from_name(fformat_name)

    fformat.export_function(filename, cat_names_to_export, \
                            reset_learning_data)

    id_to_anon = {}


