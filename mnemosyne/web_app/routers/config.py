#
# config.py <lucascontre95@gmail.com>
#

"""A curated subset of libmnemosyne settings, editable from the browser."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from mnemosyne.web_app.templating import templates

router = APIRouter()

# (key, label, kind, choices). Kept deliberately small; the full config has
# many machine-specific keys that don't belong in a simple web form.
BOOL_KEYS = [
    ("show_tags_during_review", "Show tags during review"),
    ("upload_science_logs", "Upload anonymous science logs"),
]
CHOICE_KEYS = [
    ("QA_split", "Question/answer layout",
     ["fixed", "adaptive", "single_window"]),
    ("show_intervals", "Show next-interval info",
     ["never", "status_bar", "buttons", "tooltips"]),
]
INT_KEYS = [
    ("save_after_n_reps", "Save after N repetitions"),
]


def _read(m):
    cfg = m.config()
    return {
        "bools": [(k, label, bool(cfg[k])) for k, label in BOOL_KEYS],
        "choices": [(k, label, opts, cfg[k])
                    for k, label, opts in CHOICE_KEYS],
        "ints": [(k, label, cfg[k]) for k, label in INT_KEYS],
    }


@router.get("/config", response_class=HTMLResponse)
async def config(request: Request):
    data = await request.app.state.core.call(_read)
    return templates.TemplateResponse(request, "config.html", {"d": data})


@router.post("/config")
async def save_config(request: Request):
    form = await request.form()

    def action(m):
        cfg = m.config()
        for key, _label in BOOL_KEYS:
            cfg[key] = form.get(key) is not None  # checkbox present == True
        for key, _label, opts in CHOICE_KEYS:
            value = form.get(key)
            if value in opts:
                cfg[key] = value
        for key, _label in INT_KEYS:
            try:
                cfg[key] = int(form.get(key))
            except (TypeError, ValueError):
                pass
        cfg.save()

    await request.app.state.core.call(action)
    return RedirectResponse("/config", status_code=303)
