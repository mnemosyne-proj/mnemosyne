#
# cards.py <lucascontre95@gmail.com>
#

"""Add / edit / delete cards, driven by the libmnemosyne controller."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from mnemosyne.web_app.templating import templates

router = APIRouter()


def _card_type_fields(m, card_type_id):
    card_type = m.card_type_with_id(card_type_id)
    return [(key, name) for key, name in card_type.fact_keys_and_names]


def _new_form(m, card_type_id):
    card_types = [(c.id, c.name) for c in m.card_types()]
    selected = card_type_id or card_types[0][0]
    return {
        "mode": "new",
        "action": "/cards/new",
        "card_types": card_types,
        "card_type_locked": False,
        "selected": selected,
        "fields": _card_type_fields(m, selected),
        "values": {},
        "tags": "default",
    }


def _edit_form(m, card_id):
    card = m.database().card(card_id, is_id_internal=True)
    card_type = card.card_type
    return {
        "mode": "edit",
        "action": f"/cards/{card_id}/edit",
        # Card-type conversion needs a field correspondence map; keep the type
        # fixed when editing (documented limitation for now).
        "card_types": [(card_type.id, card_type.name)],
        "card_type_locked": True,
        "selected": card_type.id,
        "fields": _card_type_fields(m, card_type.id),
        "values": dict(card.fact.data),
        "tags": card.tag_string(),
    }


def _split_tags(raw):
    tags = [t.strip() for t in (raw or "").split(",") if t.strip()]
    return tags or ["default"]


@router.get("/cards/new", response_class=HTMLResponse)
async def new_card(request: Request, card_type: str = ""):
    data = await request.app.state.core.call(
        lambda m: _new_form(m, card_type or None))
    return templates.TemplateResponse(request, "card_form.html", {"f": data})


@router.get("/cards/fields", response_class=HTMLResponse)
async def card_fields(request: Request, card_type: str):
    """Field set for a card type (HTMX swap when the type select changes)."""
    fields = await request.app.state.core.call(
        lambda m: _card_type_fields(m, card_type))
    return templates.TemplateResponse(
        request, "_fact_fields.html", {"fields": fields, "values": {}})


@router.post("/cards/new")
async def create_card(request: Request):
    form = await request.form()
    card_type_id = form.get("card_type")
    tags = _split_tags(form.get("tags"))

    def action(m):
        card_type = m.card_type_with_id(card_type_id)
        fact_data = {key: form.get(key, "")
                     for key, _name in card_type.fact_keys_and_names}
        if not card_type.is_fact_data_valid(fact_data):
            return False
        m.controller().create_new_cards(
            fact_data, card_type, grade=-1, tag_names=tags)
        m.review_controller().reset_but_try_to_keep_current_card()
        return True

    await request.app.state.core.call(action)
    return RedirectResponse("/browse", status_code=303)


@router.post("/cards/{card_id}/edit")
async def update_card(request: Request, card_id: int):
    form = await request.form()
    tags = _split_tags(form.get("tags"))

    def action(m):
        card = m.database().card(card_id, is_id_internal=True)
        card_type = card.card_type
        fact_data = {key: form.get(key, "")
                     for key, _name in card_type.fact_keys_and_names}
        if not card_type.is_fact_data_valid(fact_data):
            return False
        # Same card type -> identity correspondence.
        m.controller().edit_card_and_sisters(
            card, fact_data, card_type, tags, correspondence={})
        m.review_controller().reset_but_try_to_keep_current_card()
        return True

    await request.app.state.core.call(action)
    return RedirectResponse("/browse", status_code=303)


@router.get("/cards/{card_id}/edit", response_class=HTMLResponse)
async def edit_card(request: Request, card_id: int):
    data = await request.app.state.core.call(lambda m: _edit_form(m, card_id))
    return templates.TemplateResponse(request, "card_form.html", {"f": data})


@router.post("/cards/{card_id}/delete")
async def delete_card(request: Request, card_id: int):
    def action(m):
        db = m.database()
        card = db.card(card_id, is_id_internal=True)
        fact = db.fact(card.fact._id, is_id_internal=True)
        m.controller().delete_facts_and_their_cards(
            [fact], progress_bar=False)
        m.review_controller().reset_but_try_to_keep_current_card()

    await request.app.state.core.call(action)
    return RedirectResponse("/browse", status_code=303)
