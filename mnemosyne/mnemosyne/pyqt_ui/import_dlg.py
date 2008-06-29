##############################################################################
#
# Widget to import items <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *

from mnemosyne.core import *
from import_frm import *
from message_boxes import *



##############################################################################
#
# ImportDlg
#
##############################################################################

class ImportDlg(ImportFrm):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        
        ImportFrm.__init__(self,parent,name,modal,fl)

        for fformat in get_importable_file_formats():
            self.fileformats.insertItem(fformat.name)

        self.fileformats.setCurrentText(get_config("import_format"))

        self.categories.insertItem(self.trUtf8("<default>"))

        names = [cat.name for cat in get_categories()]
        names.sort()
        for name in names:
            if name != self.trUtf8("<default>"):
                self.categories.insertItem(name)

        self.reset_box.setChecked(get_config("reset_learning_data_import"))
        
        self.connect(self.browse_button, SIGNAL("clicked()"), self.browse)
        self.connect(self.ok_button,     SIGNAL("clicked()"), self.apply)

    ##########################################################################
    #
    # browse
    #
    ##########################################################################

    def browse(self):

        fformat = get_file_format_from_name(
                      unicode(self.fileformats.currentText()))

        out = unicode(QFileDialog.getOpenFileName(
              expand_path(get_config("import_dir")),
              self.trUtf8("All Files (*);;").append(QString(fformat.filter)),
              self, None, self.trUtf8("Import"), fformat.filter))
       
        if out != "":
            self.filename.setText(out)
            
    ##########################################################################
    #
    # apply
    #
    #   Don't rebuild the revision queue here, as the scheduled item have
    #   already been added to it during import.
    #
    ##########################################################################

    def apply(self):

        fname = unicode(self.filename.text())
        fformat_name = unicode(self.fileformats.currentText())
        cat_name = unicode(self.categories.currentText())
        reset_learning_data = self.reset_box.isChecked()

        try:
            import_file(fname, fformat_name, cat_name, reset_learning_data)
        except MnemosyneError, e:
            messagebox_errors(self, e) # Needs to be caught at this level.

        set_config("import_dir", contract_path(os.path.dirname(fname)))
        set_config("import_format", fformat_name)
        set_config("reset_learning_data_import", reset_learning_data)
        
        self.close()
