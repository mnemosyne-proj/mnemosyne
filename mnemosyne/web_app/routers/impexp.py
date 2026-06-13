#
# impexp.py <lucascontre95@gmail.com>
#

"""Import / export, driven by libmnemosyne's `file_format` components."""

import os
import tempfile

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse

from mnemosyne.web_app.templating import templates

router = APIRouter()


def _format_class(fmt):
    return fmt if isinstance(fmt, type) else type(fmt)


def _instance(m, fmt):
    if isinstance(fmt, type):
        return fmt(component_manager=m.component_manager)
    return fmt


def _entry(cls):
    return {"id": cls.__name__, "description": cls.description,
            "ext": cls.extension}


def _formats(m):
    importable, exportable = [], []
    for fmt in m.component_manager.all("file_format"):
        cls = _format_class(fmt)
        if cls.import_possible:
            importable.append(_entry(cls))
        if cls.export_possible:
            exportable.append(_entry(cls))
    return {"importable": importable, "exportable": exportable}


def _find(m, fmt_id):
    for fmt in m.component_manager.all("file_format"):
        if _format_class(fmt).__name__ == fmt_id:
            return _instance(m, fmt)
    return None


@router.get("/impexp", response_class=HTMLResponse)
async def impexp(request: Request):
    data = await request.app.state.core.call(_formats)
    return templates.TemplateResponse(request, "impexp.html", {"d": data})


@router.post("/import")
async def import_file(request: Request):
    form = await request.form()
    fmt_id = form.get("format")
    tag = (form.get("tag") or "").strip()
    upload = form.get("file")
    if upload is None or not getattr(upload, "filename", ""):
        raise HTTPException(status_code=400, detail="No file uploaded")
    contents = await upload.read()

    tmp_dir = tempfile.mkdtemp(prefix="mnem-import-")
    src = os.path.join(tmp_dir, os.path.basename(upload.filename))
    with open(src, "wb") as f:
        f.write(contents)

    def action(m):
        fmt = _find(m, fmt_id)
        if fmt is None or not _format_class(fmt).import_possible:
            return False
        # Positional arg works whether the format names it extra_tag_name(s).
        fmt.do_import(src, tag or None)
        m.database().save()
        m.review_controller().reset_but_try_to_keep_current_card()
        return True

    ok = await request.app.state.core.call(action)
    if not ok:
        raise HTTPException(status_code=400, detail="Format cannot import")
    return RedirectResponse("/browse", status_code=303)


@router.post("/export")
async def export_file(request: Request):
    form = await request.form()
    fmt_id = form.get("format")

    def action(m):
        fmt = _find(m, fmt_id)
        if fmt is None or not _format_class(fmt).export_possible:
            return None
        cls = type(fmt)
        tmp_dir = tempfile.mkdtemp(prefix="mnem-export-")
        out = os.path.join(tmp_dir, "mnemosyne-export" + (cls.extension or ""))
        fmt.do_export(out)
        return out

    out = await request.app.state.core.call(action)
    if out is None:
        raise HTTPException(status_code=400, detail="Unknown format")
    return FileResponse(out, filename=os.path.basename(out),
                        media_type="application/octet-stream")
