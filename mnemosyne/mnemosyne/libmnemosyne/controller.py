#
# controller.py <Peter.Bienstman@UGent.be>
#

from mnemosyne.libmnemosyne.component import Component


class Controller(Component):

    """A collection of logic used by the GUI.  The logic related to the
    review process is split out in a separated controller class, to
    allow that to be swapped out easily.

    The are basically two types of functions here. Functions like 'add_card',
    'edit_current_card', ... will be called by the GUI immediately when the
    user selects that option from the menu or toolbar. These functions will
    then create the corresponding dialogs, which in turn should call functions
    like 'create_new_cards', 'edit_sister_cards' to achieve the desired
    functionality.

    See 'How to write a new frontend' in documentation for more information.

    """

    component_type = "controller"

    def heartbeat(self):

        """For code that needs to run periodically."""
        
        pass

    def update_title(self):
        raise NotImplementedError        
        
    def add_cards(self):
        raise NotImplementedError

    def create_new_cards(self, fact_data, card_type, grade,
                         tag_names, check_for_duplicates=True, save=True):
        raise NotImplementedError
    
    def edit_current_card(self):
        raise NotImplementedError
    
    def edit_sister_cards(self, fact, new_fact_data, new_card_type, \
                          new_tag_names, correspondence):
        raise NotImplementedError

    def delete_current_card(self):
        raise NotImplementedError

    def delete_facts_and_their_cards(self, facts):
        raise NotImplementedError

    def clone_card_type(self, card_type, clone_name):
        raise NotImplementedError
    
    def delete_card_type(self, card_type):
        raise NotImplementedError
    
    def file_new(self):
        raise NotImplementedError
    
    def file_open(self):
        raise NotImplementedError
    
    def file_save(self):
        raise NotImplementedError
    
    def file_save_as(self):
        raise NotImplementedError

    def insert_img(self, filter):

        """Filter contains the file dialog filter with the supported
        filetypes.

        """
        
        raise NotImplementedError

    def insert_sound(self, filter):

        """Filter contains the file dialog filter with the supported
        filetypes.

        """
        
        raise NotImplementedError
    
    def insert_video(self, filter):

        """Filter contains the file dialog filter with the supported
        filetypes.

        """
        
        raise NotImplementedError
    

    def browse_cards(self):
        raise NotImplementedError        
    
    def card_appearance(self):
        raise NotImplementedError
    
    def activate_plugins(self):
        raise NotImplementedError

    def manage_card_types(self):
        raise NotImplementedError

    def show_statistics(self):
        raise NotImplementedError    
    
    def configure(self):
        raise NotImplementedError

    def import_file(self):
        raise NotImplementedError
    
    def export_file(self):
        raise NotImplementedError
    
    def sync(self):
        raise NotImplementedError
