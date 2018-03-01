#
# compile_zip.py
#

import os
import sys
import shutil
import zipfile
import compileall

# Replaces *.py files in a zip archive with compiled versions.

def compile_zip(zip_file):
    # Extract to tmp dir.
    tmp_dirname = "__TMP__"
    if os.path.exists(tmp_dirname):
        shutil.rmtree(tmp_dirname)
    with zipfile.ZipFile(zip_file) as my_zip:
        my_zip.extractall(tmp_dirname)
    # Compile python files and remove originals.
    compileall.compile_dir(tmp_dirname, legacy=True)
    for dirname, subdirlist, filelist in os.walk(tmp_dirname):
        for f in filelist:
            if f.endswith("py"):
                os.remove(os.path.join(dirname, f))
    # Recompress.
    os.remove(zip_file)
    shutil.make_archive(zip_file.replace(".zip", ""), 'zip', tmp_dirname)
    shutil.rmtree(tmp_dirname)


if __name__ == "__main__":
    compile_zip(sys.argv[1])