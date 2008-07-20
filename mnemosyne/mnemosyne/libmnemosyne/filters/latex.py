
##############################################################################
#
# process_latex
#
##############################################################################

def process_latex(latex_command):

    latex_command = latex_command.replace("&lt;", "<") 

    error_str = _("<b>Problem with latex. Are latex and dvipng installed?</b>")
    
    latexdir  = os.path.join(basedir, "latex")
    imag_name = md5.new(latex_command.encode("utf-8")).hexdigest() + ".png"
    imag_file = os.path.join(latexdir, imag_name)

    if not os.path.exists(imag_file):
        
        os.chdir(latexdir)
        
        if os.path.exists("tmp1.png"):
            os.remove("tmp1.png")
    
        f = file("tmp.tex", 'w')
        for line in file("preamble"): 
            print >> f, line,
        print >> f, latex_command.encode("utf-8")
        for line in file("postamble"): 
            print >> f, line,       
        f.close()

        os.system("latex -interaction=nonstopmode tmp.tex "+\
                  " 2>&1 1>latex_out.txt")

        f = file("dvipng")       
        os.system(f.readline().rstrip())
        f.close()

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
