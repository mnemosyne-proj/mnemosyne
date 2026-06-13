#
# browse.py <lucascontre95@gmail.com>
#

"""Card browser: searchable, paginated list of cards."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from mnemosyne.web_app.templating import templates

router = APIRouter()

PER_PAGE = 50


def _list_cards(m, query, page):
    db = m.database()
    all_ids = list(db.cards())  # (card_id, fact_id), internal ids
    if query:
        needle = query.lower()
        ids = []
        for card_id, fact_id in all_ids:
            card = db.card(card_id, is_id_internal=True)
            if any(needle in str(v).lower()
                   for v in card.fact.data.values()):
                ids.append((card_id, fact_id))
    else:
        ids = all_ids
    total = len(ids)
    pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    page = max(1, min(page, pages))
    start = (page - 1) * PER_PAGE
    rows = []
    for card_id, _fact_id in ids[start:start + PER_PAGE]:
        card = db.card(card_id, is_id_internal=True)
        rows.append({
            "id": card_id,
            "question": card.question("card_browser"),
            "answer": card.answer("card_browser"),
            "tags": card.tag_string(),
            "grade": card.grade,
            "card_type": card.card_type.name,
        })
    return {"rows": rows, "total": total, "page": page, "pages": pages,
            "query": query or ""}


@router.get("/browse", response_class=HTMLResponse)
async def browse(request: Request, q: str = "", page: int = 1):
    data = await request.app.state.core.call(
        lambda m: _list_cards(m, q, page))
    return templates.TemplateResponse(request, "browse.html", {"d": data})
