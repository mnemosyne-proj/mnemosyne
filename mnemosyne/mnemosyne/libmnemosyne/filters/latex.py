# TODO

try:
    from hashlib import md5
except ImportError:
    from md5 import md5
    

##############################################################################
#
# process_latex
#
##############################################################################

def process_latex(latex_command):
    latex_command = latex_command.replace("&lt;", "<") 
    error_str = _("<b>Problem with latex. Are latex and dvipng installed?</b>")
    latexdir = os.path.join(basedir, "latex")
    imag_name = md5(latex_command.encode("utf-8")).hexdigest() + ".png"
    imag_file = os.path.join(latexdir, imag_name)
    if not os.path.exists(imag_file):
        os.chdir(latexdir)
        if os.path.exists("tmp1.png"):
            os.remove("tmp1.png")
        f = file("tmp.tex", 'w') 
        print >> f, config()["latex_preamble"]
        print >> f, latex_command.encode("utf-8")
        print >> f, config()["latex_postamble"]           
        f.close()
        os.system(config()["latex"] + " tmp.tex 2>&1 1>latex_out.txt")     
        os.system(config()["dvipng"].rstrip())
        if not os.path.exists("tmp1.png"):
            return error_str
        shutil.copy("tmp1.png", imag_name)
    return "<img src=\"" + latexdir + "/"+imag_name+"\" align=middle>"

##############################################################################
#
# preprocess
#
#   Do some text preprocessing of Q/A strings and handle special tags.
#
##############################################################################

# The regular expressions to find the latex tags are global so they don't
# get recompiled all the time. match.group(1) identifies the text between
# the tags (thanks to the parentheses), match.group() is the text plus the
# tags.

re1 = re.compile(r"<latex>(.+?)</latex>", re.DOTALL | re.IGNORECASE)
re2 = re.compile(r"<\$>(.+?)</\$>",       re.DOTALL | re.IGNORECASE)
re3 = re.compile(r"<\$\$>(.+?)</\$\$>",   re.DOTALL | re.IGNORECASE)

def preprocess(s):

    # Process <latex>...</latex> tags.
    
    for match in re1.finditer(s):   
        imgtag = process_latex(match.group(1))
        s = s.replace(match.group(), imgtag)
    
    # Process <$>...</$> (equation) tags.

    for match in re2.finditer(s):
        imgtag = process_latex("$" + match.group(1) + "$")
        s = s.replace(match.group(), imgtag)
     
    # Process <$$>...</$$> (displaymath) tags.

    for match in re3.finditer(s):
        imgtag = process_latex("\\begin{displaymath}" + match.group(1) \
                               + "\\end{displaymath}")
        s = s.replace(match.group(), "<center>" + imgtag + "</center>")
