#
# templating.py <lucascontre95@gmail.com>
#

"""Shared Jinja2 environment, imported by both `app.py` and the routers."""

import os

from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "templates")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
