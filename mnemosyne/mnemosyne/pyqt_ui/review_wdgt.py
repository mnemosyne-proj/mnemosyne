##############################################################################
#
# Review widget <Peter.Bienstman@UGent.be>
#
##############################################################################

import gettext
_ = gettext.gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ui_review_wdgt import *


##############################################################################
#
# ReviewWdget
#
##############################################################################

class ReviewWdgt(QWidget, Ui_ReviewWdgt):
    
    ##########################################################################
    #
    # __init__
    #
    ##########################################################################
    
    def __init__(self, parent = None):
        
        QWidget.__init__(self, parent)
        self.setupUi(self)


        self.question.setHtml("""
<html>
<head>
<style type="text/css">

body {
        color: black;
        background-color: white;
        margin: 0;
        padding: 0;
        border: thin solid #8F8F8F; }

#q { font-weight: bold;
     text-align: center; }
        
#a { color: green;
     text-align: center; }
        
</style>
</head>
<body>
<table height="100%" align="center">
<tr>
<td>
<p id='q'>
question
</p>
<p id='a'>
answer
</p>

</td>
</tr>
</table>
</body>
</html>
""")
