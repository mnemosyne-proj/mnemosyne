#
# UDP_main_window.py <Peter.Bienstman@UGent.be>
#

import socket

from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class UDP_MainWindow(MainWidget):

    def __init__(self, component_manager):
        MainWidget.__init__(self, component_manager)
        self.socket = None
        self.progress_bar = None
        self.progress_bar_update_interval = 1

    def set_socket(self, socket, client_address):
        self.socket = socket
        self.client_address = client_address

    def write_to_socket(self, data):
        socket = self.component_manager.socket
        client_address = self.component_manager.client_address
        socket.sendto(data + "\nDONE\n", client_address)

    def read_from_socket(self):
        return self.component_manager.socket.makefile("rb").readline()

    def status_bar_message(self, message):
        self.status_bar.showMessage(message)

    def show_information(self, message):
        pass

    def show_question(self, question, option0, option1, option2):
        self.write_to_socket\
            ("< main_widget.show_question(\"%s\")" % question)
            return int(self.read_from_socket())
    
    def show_error(self, message):
        pass

    def set_progress_text(self, text):
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
        if not self.progress_bar:
            self.progress_bar = QtGui.QProgressDialog(self)
            self.progress_bar.setWindowTitle(_("Mnemosyne"))
            self.progress_bar.setWindowModality(QtCore.Qt.WindowModal)
            self.progress_bar.setCancelButton(None)
            self.progress_bar.setMinimumDuration(0)
        self.progress_bar.setLabelText(text)
        self.progress_bar.setRange(0, 0)
        self.progress_bar_update_interval = 1
        self.progress_bar.setValue(0)
        self.progress_bar.show()

    def set_progress_range(self, minimum, maximum):
        self.progress_bar.setRange(minimum, maximum)
        
    def set_progress_update_interval(self, update_interval):
        update_interval = int(update_interval)
        if update_interval == 0:
            update_interval = 1
        self.progress_bar_update_interval = update_interval
        
    def set_progress_value(self, value):
        if value % self.progress_bar_update_interval == 0:
            self.progress_bar.setValue(value)
        
    def close_progress(self):
        if self.progress_bar:
            self.progress_bar.close()
        self.progress_bar = None
        
    def enable_edit_current_card(self, enable):
        pass

    def enable_delete_current_card(self, enable):
        pass

    def enable_browse_cards(self, enable):      
        pass

    def save_file_dialog(self, path, filter, caption=""):
        return unicode(QtGui.QFileDialog.getSaveFileName(self, caption, path,
                                                         filter))
    
    def open_file_dialog(self, path, filter, caption=""):
        return unicode(QtGui.QFileDialog.getOpenFileName(self, caption, path,
                                                         filter))

    def set_window_title(self, title):
        self.write_to_socket\
            ("< main_widget.set_window_title(\"%s\")" % title)

    def add_cards(self):
        self.controller().add_cards()

    def edit_current_card(self):
        self.controller().edit_current_card()
        
    def delete_current_fact(self):
        self.controller().delete_current_fact()
        
    def browse_cards(self):
        self.controller().browse_cards()
        
    def activate_cards(self):
        self.controller().activate_cards()
        
    def file_new(self):
        self.controller().file_new()

    def file_open(self):
        self.controller().file_open()
        
    def file_save(self):
        self.controller().file_save()
        
    def file_save_as(self):
        self.controller().file_save_as()
        
    def manage_card_types(self):
        self.controller().manage_card_types()
        
    def card_appearance(self):
        self.controller().card_appearance()
        
    def activate_plugins(self):
        self.controller().activate_plugins()

    def show_statistics(self):
        self.controller().show_statistics()
        
    def import_file(self):
        self.controller().import_file()
        
    def export_file(self):
        self.controller().export_file()

    def sync(self):
        self.controller().sync()

    def configure(self):
        self.controller().configure()      
