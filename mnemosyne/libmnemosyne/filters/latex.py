#
# latex.py <Peter.Bienstman@gmail.com>
#

import os
import re
import subprocess as sp
import sys
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

from mnemosyne.libmnemosyne.hook import Hook
from mnemosyne.libmnemosyne.utils import copy
from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.filter import Filter

if sys.platform == "darwin":
  sys.path.append("/usr/local/bin")
  sys.path.append("/Library/TeX/texbin")

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

    def latex_img_filename(self, latex_command):
        hash_input = latex_command.rstrip() + \
            self.config()["latex_preamble"].rstrip() + \
            self.config()["latex_postamble"].rstrip() + \
            " ".join(self.config()["dvipng"]) + \
            " ".join(self.config()["latex"])
        return md5(hash_input.encode("utf-8")).hexdigest() + ".png"

    def create_latex_img_file(self, latex_command):

        """Creates png file from a latex command if needed. Returns path name
        relative to the media dir, to be stored in the media database (hence
        with the linux path name convention). Also returns a boolean saying
        whether the img file was newly created or still in the cache (needed
        to speed up syncing).

        """

        img_name = self.latex_img_filename(latex_command)
        latex_dir = os.path.join(self.database().media_dir(), "_latex")
        filename = os.path.join(latex_dir, img_name)
        rel_filename = "_latex" + "/" + img_name  # To be stored in database.
        if not os.path.exists(filename):
            if not os.path.exists(latex_dir):
                os.makedirs(latex_dir)
            previous_dir = os.getcwd()
            os.chdir(latex_dir)
            try:
                if os.path.exists("tmp1.png"):
                    os.remove("tmp1.png")
                if os.path.exists("tmp.dvi"):
                    os.remove("tmp.dvi")
                if os.path.exists("tmp.aux"):
                    os.remove("tmp.aux")
                f = open("tmp.tex", "w", encoding="utf-8")
                print(self.config()["latex_preamble"], file=f)
                print(latex_command, file=f)
                print(self.config()["latex_postamble"], file=f)
                f.close()
                in_file = "tmp.tex"
                self._call_cmd(self.config()["latex"] + [in_file],
                               "latex_out.txt", in_file)
                self._call_cmd(self.config()["dvipng"], "dvipng_out.txt")
                if not os.path.exists("tmp1.png"):
                    return None
                copy("tmp1.png", img_name)
                self.log().added_media_file(rel_filename)
            finally:
                os.chdir(previous_dir)
        return rel_filename

    def _call_cmd(self, cmd, out_file, in_file=None):
        """ Used to call latex or dvipng. """
        try:
            with open(out_file, "wb") as f:
                sp.check_call(cmd, stdout=f, stderr=sp.STDOUT, timeout=60)
        except PermissionError:
            print("Permission denied.")
        except FileNotFoundError:
            print("Could not find executable: `%s`" % " ".join(cmd))
        except sp.TimeoutExpired:
            print("Command timed out: `%s`" % " ".join(cmd))
        except sp.CalledProcessError as err:
            print("Command `%s` failed with rc=%i" % (" ".join(cmd),
                                                      err.returncode))
            with open(out_file, "r") as f:
                print("Command output:")
                print(f.read())
            if in_file:
                with open(in_file, "r") as f:
                    print("Command input:")
                    print(f.read())

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

    def run(self, text, card, fact_key, **render_args):

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


class CheckForUpdatedLatexFiles(Hook):

    # Used during sync. Added here to keep all the latex functionality in
    # a single file.

    used_for = "dynamically_create_media_files"

    def __init__(self, component_manager):
        Hook.__init__(self, component_manager)
        self.latex = Latex(component_manager)

    def is_working(self):
        try:
            p = sp.check_output(self.config()["latex"] + ["-version"],
                                stderr=sp.STDOUT, timeout=5)
            return True
        except (sp.TimeoutExpired, sp.CalledProcessError, FileNotFoundError,
                PermissionError):
            return False

    def run(self, data):
        self.latex.run(data, None, None)


class LatexFilenamesFromData(Hook):

    # Used during export. Added here to keep all the latex functionality in
    # a single file.

    used_for = "active_dynamic_media_files"
    tags = ["<latex>", "<$>", "<$$>"]

    def __init__(self, component_manager):
        Hook.__init__(self, component_manager)
        self.latex = Latex(component_manager)

    def run(self, data):
        filenames = set()
        # Process <latex>...</latex> tags.
        for match in re1.finditer(data):
            filenames.add(self.latex.create_latex_img_file(match.group(1)))
        # Process <$>...</$> (equation) tags.
        for match in re2.finditer(data):
            filenames.add(\
                self.latex.create_latex_img_file("$" + match.group(1) + "$"))
        # Process <$$>...</$$> (displaymath) tags.
        for match in re3.finditer(data):
            filenames.add(self.latex.create_latex_img_file(\
                "\\begin{displaymath}" + match.group(1) + \
                "\\end{displaymath}"))
        # Check if there were Latex problems.
        if None in filenames:
            self.main_widget().show_error(\
                    _("Problem with latex. Are latex and dvipng installed?"))
            filenames.remove(None)
        return filenames


class DeleteUnusedLatexFiles(Hook):

    used_for = "delete_unused_media_files"

    def run(self):
        # Crude approach: just delete everything.
        latex_dir = os.path.join(self.database().media_dir(), "_latex")
        import shutil
        if os.path.exists(latex_dir):
            shutil.rmtree(latex_dir)


class PreprocessClozeLatex(Hook):

    """Make sure we escape /left[ and /right]."""

    used_for = "preprocess_cloze"

    def run(self, text):
        return text.replace("\\left[", "_LEFT_BRACKET_").\
            replace("\\right]", "_RIGHT_BRACKET_")


class PostprocessQAClozeLatex(Hook):

    """Make sure we add latex tags to the answer of cloze cards."""

    used_for = "postprocess_q_a_cloze"

    def run(self, question, answer):
        # Sentence card type, recognition.
        if not "[" in question or not "]" in question:
            return question, answer
        left, rest = question.split("[", 1)
        hint, right = rest.split("]", 1)
        question = question.replace("_LEFT_BRACKET_", "\\left[",).\
            replace("_RIGHT_BRACKET_", "\\right]",)
        answer = answer.replace("_LEFT_BRACKET_", "\\left[",).\
            replace("_RIGHT_BRACKET_", "\\right]",)
        # If we pull out a cloze from within a running math environment,
        # add extra tags.
        if "<latex>" in left and not "</latex>" in left and \
            "</latex>" in right and not "<latex>" in right:
            answer = "<latex>" + answer + "</latex>"
        elif "<$>" in left and not "</$>" in left and \
            "</$>" in right and not "<$>" in right:
            answer = "<$>" + answer + "</$>"
        elif "<$$>" in left and not "</$$>" in left and \
            "</$$>" in right and not "<$$>" in right:
            answer = "<$$>" + answer + "</$$>"
        return question, answer
