
import os

def run():
    package_dir = os.path.dirname(__file__)
    exec(open(os.path.join(package_dir, "mnemosyne")).read())
