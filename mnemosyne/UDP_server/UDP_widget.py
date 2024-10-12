#
# UDP_widget.py <Peter.Bienstman@gmail.com>
#

import socket
import inspect


class UDP_Widget(object):

    """Common code for main_widget and review_widget to communicate
    callbacks to the client and get results back.

    """

    def callback(self, *args):

        """Create a string to pass to the UDP client to identify which
        function it needs to call and with which arguments, e.g.

        @@main_widget.show_question(...)

        Arguments are always triple quoted strings, utf-8 encoded.

        """

        caller_name = inspect.stack()[1][3]
        command = "@@%s.%s(" % (self.component_type, caller_name)
        for arg in args:
            command += "\"\"\"%s\"\"\"," % str(arg).encode("utf-8")
        if args:
            command = command[:-1]
        self.component_manager.socket.sendall(command + ")\n")

    def read_from_socket(self):
        return self.component_manager.socket.makefile("rb").readline()
