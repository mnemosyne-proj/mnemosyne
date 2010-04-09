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

    def latex_img_file(self, latex_command):

        """Creates png file from latex command if needed. Returns path name
        relative to the media dir, to be stored in the media database (hence
        with the linux path name convention).

        """
        
        latex_command = latex_command.replace("&lt;", "<")
        latex_command = latex_command.replace("&gt;", ">")        
        latex_dir = os.path.join(self.database().mediadir(), "latex")
        img_name = md5(latex_command.encode("utf-8")).hexdigest() + ".png"
        img_file = os.path.join(latex_dir, img_name)
        if not os.path.exists(img_file):
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
        return "latex" + "/" img_file

    def latex_img_files(self, text):

        """Processes all the latex tags in a string and returns the resulting
        filenames relative to the media dir.

        """
        
        filenames = []
        # Process <latex>...</latex> tags.
        for match in re1.finditer(text):   
            filenames.append(self.latex_img_file(match.group(1)))
        # Process <$>...</$> (equation) tags.
        for match in re2.finditer(text):
            filename.append(self.latex_img_file("$" + match.group(1) + "$"))
        # Process <$$>...</$$> (displaymath) tags.
        for match in re3.finditer(text):
            filenames.append(self.latex_img_file("\\begin{displaymath}" \
               + match.group(1) + "\\end{displaymath}"))
        if None in filenames:
            return []
        else:
            return filenames

    def process_latex_img_tag(self, latex_command):

        """Transform the latex tags to image tags."""
        
        img_file = self.latex_img_file(latex_command)
        if not img_file:
            return "<b>" + \
            _("Problem with latex. Are latex and dvipng installed?") + "</b>"
        # Note: the expanding of paths could happen in the expand_paths plugin
        # as well, but then we'd have to rely on the fact that the latex filter
        # runs first.
        img_file = os.path.join(self.database().mediadir, img_file)
        return "<img src=\"file:\\\\" + img_file + "\" align=middle>"
    
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
        
