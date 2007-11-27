##############################################################################
#
# Widget to export items <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *

from mnemosyne.core import *
from export_frm import *
from message_boxes import *



##############################################################################
#
# ExportDlg
#
##############################################################################

class ExportDlg(ExportFrm):

    ##########################################################################
    #
    # __init__
    #
    ##########################################################################

    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        
        ExportFrm.__init__(self,parent,name,modal,fl)

        for fformat in get_exportable_file_formats():
            self.fileformats.insertItem(fformat.name)
            
        self.fileformats.setCurrentText(get_config("export_format"))
        
        for cat in get_categories():
            c = QListBoxText(self.categories, cat.name)
            self.categories.setSelected(c, 1)
        self.categories.sort()

        self.reset_box.setChecked(get_config("reset_learning_data_export"))

        self.default_fname = get_config("path")[:-3]+"xml"
        self.filename.setText(self.default_fname)
        self.connect(self.browse_button, SIGNAL("clicked()"), self.browse)
        self.connect(self.all_button, SIGNAL("clicked()"), self.select_all)
        self.connect(self.ok_button, SIGNAL("clicked()"), self.apply)
     
    ##########################################################################
    #
    # browse
    #
    ##########################################################################

    def browse(self):

        fformat = get_file_format_from_name(
                      unicode(self.fileformats.currentText()))

        out = unicode(QFileDialog.getSaveFileName(
              expand_path(get_config("export_dir")),
              self.trUtf8("All Files (*);;").append(QString(fformat.filter)),
              self, None, self.trUtf8("Export"), fformat.filter))

        if out != "":
            self.filename.setText(out)

    ##########################################################################
    #
    # select_all
    #
    ##########################################################################

    def select_all(self):
        item = self.categories.firstItem()
        while item != None:
            self.categories.setSelected(item, 1)
            item = item.next()

    ##########################################################################
    #
    # apply
    #
    ##########################################################################

    def apply(self):

        fname = unicode(self.filename.text())
        
        fformat_name = unicode(self.fileformats.currentText())

        if os.path.exists(fname):   
            if not queryOverwriteFile(fname):
                return

        cat_names_to_export = []
        item = self.categories.firstItem()
        while item != None:
            if item.isSelected() == True:
                cat_names_to_export.append(unicode(item.text()))
            item = item.next()

        reset_learning_data = self.reset_box.isChecked()

        try:
            export_file(
                fname, fformat_name, cat_names_to_export, reset_learning_data)
        except MnemosyneError, e:
            messagebox_errors(e) # Needs to be caught at this level.
            
        set_config("export_dir", contract_path(os.path.dirname(fname)))
        set_config("export_format", fformat_name)
        set_config("reset_learning_data_export", reset_learning_data)

        self.close()
