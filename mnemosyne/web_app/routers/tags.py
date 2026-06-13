#
# tags.py <lucascontre95@gmail.com>
#

"""Tag management: list, rename, delete."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from mnemosyne.web_app.templating import templates

router = APIRouter()


def _list_tags(m):
    return [{"id": t._id, "name": t.name} for t in m.database().tags()]


@router.get("/tags", response_class=HTMLResponse)
async def tags(request: Request):
    data = await request.app.state.core.call(_list_tags)
    return templates.TemplateResponse(request, "tags.html", {"tags": data})


@router.post("/tags/{tag_id}/rename")
async def rename_tag(request: Request, tag_id: int):
    form = await request.form()
    new_name = (form.get("name") or "").strip()

    def action(m):
        if not new_name:
            return
        db = m.database()
        tag = db.tag(tag_id, is_id_internal=True)
        tag.name = new_name
        db.update_tag(tag)
        db.save()

    await request.app.state.core.call(action)
    return RedirectResponse("/tags", status_code=303)


@router.post("/tags/{tag_id}/delete")
async def delete_tag(request: Request, tag_id: int):
    def action(m):
        db = m.database()
        tag = db.tag(tag_id, is_id_internal=True)
        db.delete_tag(tag)
        db.save()

    await request.app.state.core.call(action)
    return RedirectResponse("/tags", status_code=303)
