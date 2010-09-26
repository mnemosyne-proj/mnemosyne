#
# UDP_main_widget.py <Peter.Bienstman@UGent.be>
#

import sys
import socket

from mnemosyne.libmnemosyne.ui_components.main_widget import MainWidget


class UDP_MainWidget(MainWidget):

    def __init__(self, component_manager):
        MainWidget.__init__(self, component_manager)
        self.socket = None

    def set_socket(self, socket, client_address):
        self.socket = socket
        self.client_address = client_address
        sys.stdout = socket
        sys.stderr = socket

    def write_to_socket(self, data):
        socket = self.component_manager.socket
        client_address = self.component_manager.client_address
        socket.sendto(data + "\n", client_address)

    def read_from_socket(self):
        return self.component_manager.socket.makefile("rb").readline()

    def status_bar_message(self, message):
        self.status_bar.showMessage(message)

    def show_information(self, message):
        self.write_to_socket\
            ("@@main_widget.show_information(\"%s\")" % message)

    def show_question(self, question, option0, option1, option2):
        self.write_to_socket\
            ("@@main_widget.show_question(\"%s\")" % question)
        return int(self.read_from_socket())
    
    def show_error(self, message):
        self.write_to_socket\
            ("@@main_widget.show_error(\"%s\")" % message)

    def set_progress_text(self, text):
        pass

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
            ("@@main_widget.set_window_title(\"%s\")" % title)
