##############################################################################
#
# Widget to export items <Peter.Bienstman@UGent.be>
#
##############################################################################

from qt import *

from mnemosyne.core import *
from export_frm import *



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

        for cat in get_categories():
            c = QListBoxText(self.categories, cat.name)
            self.categories.setSelected(c, 1)
        self.categories.sort()

        self.default_fname = get_config("path")[:-3]+"xml"
        self.filename.setText(self.default_fname)
        self.connect(self.browse_button, SIGNAL("clicked()"), self.browse)
        self.connect(self.all_button, SIGNAL("clicked()"), self.select_all )
        self.connect(self.ok_button, SIGNAL("clicked()"), self.apply)
     
    ##########################################################################
    #
    # browse
    #
    ##########################################################################

    def browse(self):

        out = unicode(QFileDialog.getSaveFileName(self.default_fname,\
                                         "(*.xml *.XML *.txt *.TXT)"))
        if out != "":
            
            if out[-4:] != ".xml":
                out += ".xml"

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

        fname = unicode(self.filename.text()).encode("utf-8")

        if os.path.exists(fname):
            status = QMessageBox.warning(None,
                    self.trUtf8(""),
                    self.trUtf8("""Overwrite existing file?"""),
                    self.trUtf8("&Yes"), self.trUtf8("&No"),
                    QString(), 1, -1)
            if status == 1:
                return

        cat_names_to_export = []
        item = self.categories.firstItem()
        while item != None:
            if item.isSelected() == True:
                cat_names_to_export.append(unicode(item.text()))
            item = item.next()

        reset_learning_data = self.reset_box.isChecked()

        export_file(fname, cat_names_to_export, reset_learning_data)

        self.close()
        

                
