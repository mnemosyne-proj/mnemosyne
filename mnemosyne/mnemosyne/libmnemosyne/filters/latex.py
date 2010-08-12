#
# latex.py <Peter.Bienstman@UGent.be>
#

import os
import re
import shutil
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.filter import Filter


# The regular expressions to find the latex tags are global so they don't
# get recompiled all the time. match.group(1) identifies the text between
# the tags (thanks to the parentheses), match.group() is the text plus the
# tags.

re1 = re.compile(r"<latex>(.+?)</latex>", re.DOTALL | re.IGNORECASE)
re2 = re.compile(r"<\$>(.+?)</\$>",       re.DOTALL | re.IGNORECASE)
re3 = re.compile(r"<\$\$>(.+?)</\$\$>",   re.DOTALL | re.IGNORECASE)


class Latex(Filter):

    # To create the images, we have two options: either precreate them when
    # adding or editing cards, or lazily create them before display or sync.
    # We choose the latter, so that a power user can e.g. change the latex
    # settings, delete the cached images and still have them automatically
    # regenerated as needed. The alternative would require a
    # 'rebuild latex cache' menu option, which would complicate the GUI for
    # the casual user.

    def create_latex_img_file(self, latex_command):

        """Creates png file from a latex command if needed. Returns path name
        relative to the media dir, to be stored in the media database (hence
        with the linux path name convention). Also returns a boolean saying
        whether the img file was newly created or still in the cache (needed
        to speed up syncing).

        """
     
        img_name = md5(latex_command.encode("utf-8")).hexdigest() + ".png"
        latex_dir = os.path.join(self.database().media_dir(), "latex")
        filename = os.path.join(latex_dir, img_name)
        rel_filename = "latex" + "/" + img_name # To be stored in database.
        if not os.path.exists(filename):
            previous_dir = os.getcwd()
            os.chdir(latex_dir)
            if os.path.exists("tmp1.png"):
                os.remove("tmp1.png")
            f = file("tmp.tex", 'w') 
            print >> f, self.config()["latex_preamble"]
            print >> f, latex_command.encode("utf-8")
            print >> f, self.config()["latex_postamble"]           
            f.close()
            os.system(self.config()["latex"] + " tmp.tex 2>&1 1>latex_out.txt")
            os.system(self.config()["dvipng"].rstrip())
            if not os.path.exists("tmp1.png"):
                return None
            shutil.copy("tmp1.png", img_name)
            self.log().added_media(rel_filename)
            os.chdir(previous_dir)            
        return rel_filename

    def process_latex_img_tag(self, latex_command):

        """Transform the latex tags to image tags."""
        
        img_file = self.create_latex_img_file(latex_command)
        if not img_file:
            return "<b>" + \
            _("Problem with latex. Are latex and dvipng installed?") + "</b>"
        # Note that we leave the the expanding of paths to the expand_paths
        # plugin, as during export, we should not do this and we disable the
        # expand_paths plugin. This means however that the expand_paths plugin
        # should always run at the end.
        return "<img src=\"" + img_file + "\" align=middle>"
    
    def run(self, text):

        """The actual filter code called on the question or answer text."""
        
        # Process <latex>...</latex> tags.
        for match in re1.finditer(text):   
            img_tag = self.process_latex_img_tag(match.group(1))
            text = text.replace(match.group(), img_tag)
        # Process <$>...</$> (equation) tags.
        for match in re2.finditer(text):
            img_tag = self.process_latex_img_tag("$" + match.group(1) + "$")
            text = text.replace(match.group(), img_tag)
        # Process <$$>...</$$> (displaymath) tags.
        for match in re3.finditer(text):
            img_tag = self.process_latex_img_tag("\\begin{displaymath}" \
                       + match.group(1) + "\\end{displaymath}")
            text = text.replace(match.group(), "<center>" \
                       + img_tag + "</center>")
        return text