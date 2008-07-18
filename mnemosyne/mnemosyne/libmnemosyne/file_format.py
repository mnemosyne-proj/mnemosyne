##############################################################################
#
# Mnemosyne core <Peter.Bienstman@UGent.be>, Dirk Hermann
#
##############################################################################

import_time_of_start = None # TODO: move to where it belongs.

##############################################################################
#
# FileFormat
#
# Each file format that Mnemosyne supports is identified by a name (a string).
# Additionally, a file format needs a file name filter (a string), a function
# to import data from a file of the respective type, and a function to export
# data in the respective format.
#
# The file format name will appear in the import and export dialogues.
# Therefore, they shall be easy to understand by a user, e.g. "Text
# with tab-separated Q/A".
#
# The file name filter has to be given in Qt format, e. g. "XML Files (*.xml
# *XML)". It will be used in the file selection dialogues.
#
##############################################################################

file_formats = []

class FileFormat:

    def __init__(self, name, filter="",
                 import_function=False, export_function=False):

        self.name = name
        self.filter = filter
        self.import_function = import_function
        self.export_function = export_function



##############################################################################
#
# register_file_format
#
##############################################################################

def register_file_format(name, filter="",
                         import_function=False, export_function=False):

    global file_formats
    
    file_formats.append(FileFormat(name, filter,
                                   import_function, export_function))
    
    file_formats.sort(lambda x,y: cmp(x.name, y.name))



##############################################################################
#
# unregister_file_format
#
##############################################################################

def unregister_file_format(name):

    global file_formats
    
    file_formats.remove(get_file_format_from_name(name))

	

##############################################################################
#
# get_importable_file_formats
#
##############################################################################

def get_importable_file_formats():
     return [f for f in file_formats if f.import_function]



##############################################################################
#
# get_exportable_file_formats
#
##############################################################################

def get_exportable_file_formats():
     return [f for f in file_formats if f.export_function]



##############################################################################
#
# get_file_format_from_name
#
##############################################################################

def get_file_format_from_name(name):

    for fformat in file_formats:
        if name == fformat.name:
            return fformat

    raise InvalidFormatError()



