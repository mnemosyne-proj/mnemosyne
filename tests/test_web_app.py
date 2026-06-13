#
# test_web_app.py <lucascontre95@gmail.com>
#

"""End-to-end tests for the FastAPI + HTMX web app.

These exercise the real `libmnemosyne` core through `CoreService`'s single
worker thread -- no Qt is involved, so they run anywhere FastAPI is installed.
"""

import asyncio
import tempfile

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from mnemosyne.web_app.app import create_app, Settings


def _add_cards(m):
    """Inject a few Front-to-back cards and rebuild the review queue."""
    card_type = m.card_type_with_id("1")
    for front, back in [("bonjour", "hello"), ("merci", "thanks"),
                        ("chat", "cat")]:
        m.controller().create_new_cards(
            {"f": front, "b": back}, card_type, grade=-1,
            tag_names=["default"])
    m.review_controller().reset()
    return m.review_controller().counters()


@pytest.fixture
def client():
    tmp = tempfile.mkdtemp(prefix="mnem-web-test-")
    app = create_app(Settings(data_dir=tmp))
    with TestClient(app) as client:
        yield client


def _inject(client, fn):
    """Run a function on the core worker thread from the test."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(client.app.state.core.call(fn))
    finally:
        loop.close()


def test_dashboard_renders(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Scheduled" in r.text


def test_media_traversal_is_blocked(client):
    assert client.get("/media/missing.png").status_code == 404
    assert client.get("/media/../../etc/passwd").status_code == 404


def test_review_loop(client):
    scheduled, not_memorised, active = _inject(client, _add_cards)
    assert active == 3

    r = client.get("/review")
    assert r.status_code == 200
    assert "Show answer" in r.text

    r = client.post("/review/show-answer")
    assert r.status_code == 200
    assert "grade-0" in r.text and "grade-5" in r.text

    r = client.post("/review/grade/4")
    assert r.status_code == 200
    # Either the next question or the finished state.
    assert ("Show answer" in r.text) or ("No more cards" in r.text)


def test_browse_search_and_crud(client):
    _inject(client, _add_cards)

    # Browse lists the cards.
    r = client.get("/browse")
    assert r.status_code == 200
    assert "bonjour" in r.text and "merci" in r.text

    # Search narrows results.
    r = client.get("/browse", params={"q": "chat"})
    assert "chat" in r.text and "bonjour" not in r.text

    # Add a card.
    r = client.post("/cards/new", data={
        "card_type": "1", "f": "pomme", "b": "apple", "tags": "fruit"},
        follow_redirects=False)
    assert r.status_code == 303
    assert "pomme" in client.get("/browse").text

    # Find its internal id and edit it.
    def find(m):
        for cid, _fid in m.database().cards():
            card = m.database().card(cid, is_id_internal=True)
            if card.fact["f"] == "pomme":
                return cid
        return None
    cid = _inject(client, find)
    assert cid is not None
    r = client.post(f"/cards/{cid}/edit", data={
        "f": "pomme", "b": "APPLE!", "tags": "fruit"},
        follow_redirects=False)
    assert r.status_code == 303
    assert "APPLE!" in client.get("/browse").text

    # Delete it.
    r = client.post(f"/cards/{cid}/delete", follow_redirects=False)
    assert r.status_code == 303
    assert "pomme" not in client.get("/browse").text


def test_card_form_pages_render(client):
    # Add form (regression: dict "values" key must not collide with
    # dict.values via Jinja attribute access).
    assert client.get("/cards/new").status_code == 200
    assert client.get("/cards/fields", params={"card_type": "1"}).status_code \
        == 200
    # Edit form for an existing card.
    _inject(client, _add_cards)

    def first_id(m):
        return next(iter(m.database().cards()))[0]
    cid = _inject(client, first_id)
    r = client.get(f"/cards/{cid}/edit")
    assert r.status_code == 200
    assert "Edit card" in r.text


def test_tags_page(client):
    _inject(client, _add_cards)
    r = client.get("/tags")
    assert r.status_code == 200
    assert "default" in r.text


def test_decks_list_create_switch(client):
    _inject(client, _add_cards)

    r = client.get("/decks")
    assert r.status_code == 200
    assert "default.db" in r.text

    # Create and switch to a new empty deck.
    r = client.post("/decks/create", data={"name": "spanish"},
                    follow_redirects=False)
    assert r.status_code == 303
    page = client.get("/decks").text
    assert "spanish.db" in page

    # The new deck is empty; the original cards are not present.
    assert "bonjour" not in client.get("/browse").text

    # Switch back to the original deck and confirm the cards return.
    r = client.post("/decks/switch", data={"filename": "default.db"},
                    follow_redirects=False)
    assert r.status_code == 303
    assert "bonjour" in client.get("/browse").text


def test_stats_page_and_png(client):
    _inject(client, _add_cards)
    r = client.get("/stats")
    assert r.status_code == 200
    assert "Statistics" in r.text

    # PNG rendering needs matplotlib (numpy C-extensions). Skip if the
    # environment can't load them (e.g. a bare sandbox without libstdc++);
    # the data preparation above already exercised the core code path.
    pytest.importorskip("matplotlib.backends.backend_agg")
    img = client.get("/stats/0.png")
    assert img.status_code == 200
    assert img.headers["content-type"] == "image/png"
    assert img.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_export_roundtrip(client):
    _inject(client, _add_cards)
    r = client.get("/impexp")
    assert r.status_code == 200
    # Export to tab-separated text (pure-Python, no numpy needed).
    r = client.post("/export", data={"format": "Tsv"},
                    follow_redirects=False)
    assert r.status_code == 200
    body = r.content.decode("utf-8", "replace")
    assert "bonjour" in body and "hello" in body


def test_export_mnemosyne_cards_without_dialog(client):
    # *.cards export asks for metadata via a dialog the web frontend can't
    # show; WebMainWidget must supply empty metadata instead of crashing.
    _inject(client, _add_cards)
    r = client.post("/export", data={"format": "Mnemosyne2Cards"},
                    follow_redirects=False)
    assert r.status_code == 200
    assert len(r.content) > 0


def test_export_rejects_import_only_format(client):
    # Mnemosyne2Db is import-only (no do_export); a crafted request must get a
    # clean 400, not a 500.
    _inject(client, _add_cards)
    r = client.post("/export", data={"format": "Mnemosyne2Db"},
                    follow_redirects=False)
    assert r.status_code == 400


def test_import_tsv(client):
    r = client.get("/impexp")
    assert "Tab-separated" in r.text or "Tsv" in r.text
    payload = b"hola\thi\nadios\tbye\n"
    r = client.post(
        "/import",
        data={"format": "Tsv", "tag": "spanish"},
        files={"file": ("words.txt", payload, "text/plain")},
        follow_redirects=False)
    assert r.status_code == 303
    browse = client.get("/browse").text
    assert "hola" in browse and "adios" in browse


def test_config_read_and_save(client):
    r = client.get("/config")
    assert r.status_code == 200
    assert "Settings" in r.text
    # Toggle save_after_n_reps and a choice; confirm persisted.
    r = client.post("/config", data={
        "save_after_n_reps": "7", "QA_split": "adaptive",
        "show_intervals": "never"}, follow_redirects=False)
    assert r.status_code == 303
    value = _inject(client, lambda m: (
        m.config()["save_after_n_reps"], m.config()["QA_split"]))
    assert value == (7, "adaptive")


def test_auth_token_required_when_set():
    tmp = tempfile.mkdtemp(prefix="mnem-web-auth-")
    app = create_app(Settings(data_dir=tmp, auth_token="s3cret"))
    with TestClient(app) as client:
        assert client.get("/").status_code == 401
        assert client.get(
            "/", headers={"x-auth-token": "s3cret"}).status_code == 200
