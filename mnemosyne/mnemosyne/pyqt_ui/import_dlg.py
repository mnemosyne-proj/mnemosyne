##############################################################################
#
# Widget to import items <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *

from mnemosyne.core import *
from import_frm import *



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
        self.fileformats.setCurrentText("Text with tab separated Q/A")

        self.categories.insertItem("<default>")
        for cat in get_categories():
            if cat.name != "<default>":
                self.categories.insertItem(cat.name)
        
        self.connect(self.browse_button, SIGNAL("clicked()"), self.browse)
        self.connect(self.ok_button, SIGNAL("clicked()"), self.apply)

    ##########################################################################
    #
    # browse
    #
    ##########################################################################

    def browse(self):

        fformat = get_file_format_from_name(
                      unicode(self.fileformats.currentText()))

        out = unicode(QFileDialog.getOpenFileName(
                  get_config("import_dir"),
                  "All Files (*);;" + fformat.filter,
                  None,
                  None,
                  QString(),
                  fformat.filter))
       
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

        fname = unicode(self.filename.text()).encode("utf-8")
        fformat_name = unicode(self.fileformats.currentText())
        cat_name = unicode(self.categories.currentText())
        reset_learning_data = self.reset_box.isChecked()
        status = import_file(
                     fname, fformat_name, cat_name, reset_learning_data)

        if status == False:
            QMessageBox.critical(None,
                 self.trUtf8("Mnemosyne"),
                 self.trUtf8("File doesn't appear to be in " +\
                             "the correct format."),
                 self.trUtf8("&OK"), QString(), QString(), 0, -1)
        else:
            set_config("import_dir", os.path.dirname(fname))
        
        self.close()
