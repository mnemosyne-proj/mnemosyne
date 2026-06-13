#
# decks.py <lucascontre95@gmail.com>
#

"""Multiple decks: each deck is a `.db` file in the data dir. Only one is open
at a time (the single-connection constraint), so switching saves the current
deck and loads another. Also lists the deck's saved sets (criteria)."""

import os

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from mnemosyne.web_app.templating import templates

router = APIRouter()


def _deck_state(m):
    data_dir = m.config().data_dir
    current = os.path.basename(m.database()._path) if m.database()._path \
        else ""
    files = sorted(f for f in os.listdir(data_dir)
                   if f.endswith(".db") and not f.startswith("config"))
    criteria = [c.name for c in m.database().criteria()]
    return {"data_dir": data_dir, "current": current, "files": files,
            "criteria": criteria}


@router.get("/decks", response_class=HTMLResponse)
async def decks(request: Request):
    data = await request.app.state.core.call(_deck_state)
    return templates.TemplateResponse(request, "decks.html", {"d": data})


@router.post("/decks/switch")
async def switch_deck(request: Request):
    form = await request.form()
    filename = (form.get("filename") or "").strip()
    if filename:
        # Confine to a bare filename within the data dir.
        filename = os.path.basename(filename)
        await request.app.state.core.switch_database(filename, create=False)
    return RedirectResponse("/decks", status_code=303)


@router.post("/decks/create")
async def create_deck(request: Request):
    form = await request.form()
    name = (form.get("name") or "").strip()
    if name:
        name = os.path.basename(name)
        if not name.endswith(".db"):
            name += ".db"
        await request.app.state.core.switch_database(name, create=True)
    return RedirectResponse("/decks", status_code=303)
